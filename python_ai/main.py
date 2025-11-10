"""
Therapy Bot - Main Application

This is the entry point for the therapy bot API.
It uses FastAPI to provide HTTP endpoints for:
1. Receiving user messages (SMS webhook simulation)
2. Routing to appropriate expert via MoE
3. Crisis detection and intervention
4. Conversation history management

Architecture Flow:
User Message -> Crisis Detection -> Semantic Routing -> Expert Response -> Save to DB

API Endpoints:
- POST /message - Main endpoint for user messages
- GET /health - Health check
- GET /stats/{user_id} - User statistics
- POST /test-routing - Test the semantic router
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, List
import logging
from contextlib import asynccontextmanager

# Import our modules
from config import settings
from logging_config import setup_logging
from database import init_db, close_db, get_db
from safety import detect_crisis, generate_crisis_response, get_safety_summary
from routers import router, get_router
from memory.conversation import (
    get_conversation_history,
    save_message,
    get_or_create_user,
    increment_message_count,
    check_rate_limit,
    get_recent_context_summary,
)
from database import SafetyIncident, User
from experts.cbt_expert import get_cbt_expert
from experts.mindfulness_expert import get_mindfulness_expert
from experts.motivation_expert import get_motivation_expert
from experts.claude_expert import get_claude_expert
from personalization import get_personalization_engine
from event_extraction import get_event_extractor
from scheduler import get_scheduler, start_scheduler, stop_scheduler
from sms_handler import get_sms_handler

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


# ==================== Lifespan Management ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    This handles startup and shutdown tasks:
    - Startup: Initialize database, load models
    - Shutdown: Close database connections

    Why use lifespan?
    - Ensures clean initialization/cleanup
    - Resources are ready before first request
    - Proper shutdown prevents data loss
    """
    # Startup
    logger.info("="*60)
    logger.info("THERAPY BOT STARTUP")
    logger.info("="*60)

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Display safety configuration
    logger.info("\n" + get_safety_summary())

    # Test routing (optional, useful for debugging)
    if settings.environment == "development":
        logger.info("\nTesting semantic router...")
        test_router = get_router()
        test_router.test_routing()

    # Start proactive scheduler
    logger.info("Starting proactive outreach scheduler...")
    start_scheduler()

    # Check SMS configuration
    sms_handler = get_sms_handler()
    if sms_handler.is_enabled():
        logger.info(f"SMS enabled with Twilio number: {sms_handler.from_number}")
    else:
        logger.warning("SMS not configured - running in demo mode")

    logger.info("\n" + "="*60)
    logger.info(f"Therapy Bot ready on http://{settings.host}:{settings.port}")
    logger.info("="*60 + "\n")

    yield  # Application runs

    # Shutdown
    logger.info("Shutting down Therapy Bot...")
    stop_scheduler()
    await close_db()
    logger.info("Shutdown complete")


# ==================== FastAPI App ====================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered therapy chatbot with crisis detection and MoE routing",
    lifespan=lifespan
)


# ==================== Pydantic Models ====================

class MessageRequest(BaseModel):
    """
    Request model for incoming messages

    In production SMS integration:
    - user: Phone number (hashed for privacy)
    - message: SMS text content
    """
    user: str = Field(..., description="User identifier (phone number or username)")
    message: str = Field(..., min_length=1, max_length=2000, description="User's message text")

    class Config:
        json_schema_extra = {
            "example": {
                "user": "+15551234567",
                "message": "I've been feeling really anxious lately"
            }
        }


class MessageResponse(BaseModel):
    """Response model for message endpoint"""
    reply: str = Field(..., description="Bot's response")
    expert_used: Optional[str] = Field(None, description="Which expert handled this (cbt/mindfulness/motivation)")
    routing_confidence: Optional[float] = Field(None, description="Confidence score for routing (0-1)")
    crisis_detected: bool = Field(False, description="Whether crisis content was detected")
    crisis_type: Optional[str] = Field(None, description="Type of crisis if detected")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    environment: str
    crisis_detection: bool


class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    user_id: str
    total_messages: int
    is_flagged: bool
    recent_activity: Dict
    conversation_preview: List[Dict]


class TwilioWebhookRequest(BaseModel):
    """
    Request model for Twilio SMS webhook

    Twilio sends these fields with incoming SMS messages
    """
    From: str = Field(..., description="Sender's phone number (E.164 format)")
    Body: str = Field(..., description="Message text content")
    MessageSid: Optional[str] = Field(None, description="Twilio message ID")

    class Config:
        json_schema_extra = {
            "example": {
                "From": "+15551234567",
                "Body": "I've been feeling anxious lately",
                "MessageSid": "SM1234567890abcdef"
            }
        }


# ==================== API Endpoints ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - health check

    Returns basic application status
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "crisis_detection": settings.crisis_detection_enabled,
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Detailed health check endpoint

    Use this for monitoring and alerting
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "crisis_detection": settings.crisis_detection_enabled,
    }


@app.post("/message", response_model=MessageResponse)
async def handle_message(
    request: MessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main message handling endpoint

    This is the core of the therapy bot. It:
    1. Checks rate limits
    2. Detects crisis situations
    3. Routes to appropriate expert via MoE
    4. Generates response
    5. Saves conversation history

    Flow Diagram:
    
     User Message
    ,
           
    ->
     Rate Limit? -> Reject if exceeded
    ,
           
    ->
    Crisis Check -> Crisis Response (skip MoE)
    ,
           
    ->
       MoE Route -> Select Expert
    ,
           
    ->
    Expert Reply -> Generate Response
    ,
           
    ->
      Save to DB 
    ,
           
    ->
    Return Reply 
    

    Args:
        request: MessageRequest with user ID and message
        db: Database session (injected)

    Returns:
        MessageResponse with bot reply and metadata
    """

    user_identifier = request.user
    user_message = request.message

    logger.info(f"Received message from user: {user_identifier}")
    logger.debug(f"Message content: {user_message}")

    try:
        # ==================== Step 1: Get or Create User ====================
        user, is_new = await get_or_create_user(db, user_identifier)

        if is_new:
            logger.info(f"New user created: {user_identifier}")
            welcome_note = "\n\n*Welcome! I'm here to provide supportive conversations. Remember, I'm an AI and not a replacement for professional therapy.*"
        else:
            welcome_note = ""

        # ==================== Step 2: Rate Limiting ====================
        is_allowed, remaining = await check_rate_limit(
            db,
            user.id,
            window_minutes=60,
            max_messages=settings.max_messages_per_hour
        )

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for user {user_identifier}")
            raise HTTPException(
                status_code=429,
                detail=f"Message limit reached. You can send {settings.max_messages_per_hour} messages per hour. Please try again later."
            )

        # ==================== Step 3: Crisis Detection ====================
        is_crisis, crisis_info = detect_crisis(user_message)

        if is_crisis:
            logger.warning(f"CRISIS DETECTED for user {user_identifier}: {crisis_info['type']}/{crisis_info['severity']}")

            # Save the user message first
            user_msg = await save_message(db, user.id, "user", user_message)

            # Generate crisis response
            crisis_response = generate_crisis_response(crisis_info)

            # Save crisis response
            await save_message(db, user.id, "assistant", crisis_response, expert_used="crisis")

            # Log safety incident
            incident = SafetyIncident(
                user_id=user.id,
                message_id=user_msg.id,
                incident_type=crisis_info['type'],
                severity=crisis_info['severity'],
                detected_keywords=str(crisis_info['keywords']),
                action_taken="Provided crisis resources and hotline information",
                resolved=False,
            )
            db.add(incident)

            # Flag the user for follow-up
            user.is_flagged = True

            # Increment message count
            await increment_message_count(db, user.id)

            await db.commit()

            return MessageResponse(
                reply=crisis_response + welcome_note,
                expert_used="crisis",
                routing_confidence=1.0,
                crisis_detected=True,
                crisis_type=crisis_info['type'],
            )

        # ==================== Step 4: Get Conversation Context ====================
        conversation_history = await get_conversation_history(db, user.id, limit=10)

        # ==================== Step 5: Semantic Routing (MoE) ====================
        semantic_router = get_router()
        expert_name, confidence, routing_metadata = semantic_router.route(user_message)

        logger.info(f"Routed to {expert_name} with confidence {confidence:.3f}")
        logger.debug(f"Routing metadata: {routing_metadata}")

        # ==================== Step 6: Generate Expert Response ====================
        # Check if Claude AI is available and should be used
        claude_expert = get_claude_expert()
        use_claude = not settings.use_mock_models and claude_expert.is_available()

        if use_claude:
            # Use Claude for conversational, empathetic responses
            logger.info(f"Using Claude AI for {expert_name} response")
            routing_metadata['expert'] = expert_name  # Pass expert type to Claude
            bot_response = claude_expert.generate_response(
                user_message,
                conversation_history,
                context=routing_metadata
            )
        else:
            # Use rule-based experts (fallback or demo mode)
            if expert_name == "cbt":
                expert = get_cbt_expert()
            elif expert_name == "mindfulness":
                expert = get_mindfulness_expert()
            elif expert_name == "motivation":
                expert = get_motivation_expert()
            else:
                logger.error(f"Unknown expert: {expert_name}, falling back to CBT")
                expert = get_cbt_expert()
                expert_name = "cbt"

            # Generate response
            bot_response = expert.generate_response(
                user_message,
                conversation_history,
                context=routing_metadata
            )

        # ==================== Step 6.5: Extract Events & Apply Personalization ====================
        # Extract any important events mentioned
        if settings.enable_personalization:
            event_extractor = get_event_extractor()
            events = event_extractor.extract_events(user_message)

            if events:
                logger.info(f"Extracted {len(events)} event(s) from message")
                for event in events:
                    saved_event = await event_extractor.save_event(db, user.id, event)
                    if saved_event:
                        # Add a note about tracking the event
                        bot_response += f"\n\nI've made a note about your {event['type']} on {event['date'].strftime('%A, %B %d')}. I'll check in with you about it!"

            # Get or analyze user's communication style
            personalization_engine = get_personalization_engine()

            # Analyze style every 10 messages
            if user.message_count % 10 == 0:
                user_style = await personalization_engine.analyze_user_style(db, user.id)
                await personalization_engine.save_user_style(db, user.id, user_style)
                logger.debug(f"Updated communication style for user {user.id}")
            else:
                user_style = await personalization_engine.get_user_style(db, user.id)

            # Adapt response to user's style
            bot_response = personalization_engine.adapt_response(bot_response, user_style)

        # ==================== Step 7: Save to Database ====================
        # Save user message
        await save_message(db, user.id, "user", user_message)

        # Save bot response
        await save_message(db, user.id, "assistant", bot_response, expert_used=expert_name)

        # Increment message count
        await increment_message_count(db, user.id)

        await db.commit()

        # ==================== Step 8: Return Response ====================
        return MessageResponse(
            reply=bot_response + welcome_note,
            expert_used=expert_name,
            routing_confidence=confidence,
            crisis_detected=False,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like rate limiting)
        raise

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing your message")


@app.get("/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for a specific user

    Useful for:
    - User dashboard
    - Analytics
    - Support/moderation

    Args:
        user_id: User identifier

    Returns:
        UserStatsResponse with user statistics
    """

    # Find user
    from sqlalchemy import select
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get recent activity summary
    recent_activity = await get_recent_context_summary(db, user.id, window_minutes=60)

    # Get conversation preview
    conversation_preview = await get_conversation_history(db, user.id, limit=5)

    return UserStatsResponse(
        user_id=user.user_id,
        total_messages=user.message_count,
        is_flagged=user.is_flagged,
        recent_activity=recent_activity,
        conversation_preview=conversation_preview,
    )


@app.post("/test-routing")
async def test_routing(message: str):
    """
    Test endpoint for semantic routing

    Use this to test which expert would handle a given message.
    Useful for debugging and tuning routing.

    Args:
        message: Test message

    Returns:
        Routing decision with scores for all experts

    Example:
        POST /test-routing?message=I'm feeling anxious
        Returns: {
            "message": "I'm feeling anxious",
            "routed_to": "cbt",
            "confidence": 0.82,
            "all_scores": {"cbt": 0.82, "mindfulness": 0.45, "motivation": 0.23}
        }
    """

    semantic_router = get_router()
    expert_name, confidence, metadata = semantic_router.route(message)

    return {
        "message": message,
        "routed_to": expert_name,
        "confidence": round(confidence, 3),
        "all_scores": {k: round(v, 3) for k, v in metadata['all_scores'].items()},
        "routing_reason": metadata['routing_reason'],
    }


@app.post("/sms/webhook")
async def sms_webhook(
    From: str = "",
    Body: str = "",
    MessageSid: str = "",
    db: AsyncSession = Depends(get_db)
):
    """
    Twilio SMS Webhook Endpoint

    This endpoint receives incoming SMS messages from Twilio.
    Twilio sends data as application/x-www-form-urlencoded,
    so we use Form parameters instead of a Pydantic model.

    Setup in Twilio:
    1. Go to Phone Numbers -> Active Numbers
    2. Select your number
    3. Under Messaging, set Webhook URL to:
       https://yourdomain.com/sms/webhook
    4. Method: POST

    Args:
        From: Sender's phone number (E.164 format: +15551234567)
        Body: Message text
        MessageSid: Twilio message ID

    Returns:
        TwiML response (empty for now, bot replies proactively)
    """

    logger.info(f"Received SMS from {From}: {Body[:50]}...")

    try:
        # Process message using existing message handler
        request = MessageRequest(user=From, message=Body)
        response = await handle_message(request, db)

        # Send response via SMS
        sms_handler = get_sms_handler()
        if sms_handler.is_enabled():
            success, result = await sms_handler.send_sms(
                to_number=From,
                message=response.reply
            )

            if success:
                logger.info(f"SMS reply sent to {From}: SID={result}")
            else:
                logger.error(f"Failed to send SMS reply to {From}: {result}")

        # Return empty TwiML response (Twilio requires a response)
        from fastapi.responses import Response
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}", exc_info=True)

        # Return error TwiML
        from fastapi.responses import Response
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Message>Sorry, there was an error processing your message. Please try again.</Message></Response>',
            media_type="application/xml"
        )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Custom handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred"}
    )


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
