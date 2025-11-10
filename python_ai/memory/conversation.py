"""
Conversation Memory and Context Management

This module manages conversation history and context for therapy sessions.
It retrieves recent messages, formats them for context, and manages session state.

Why conversation memory matters in therapy:
1. Continuity: Users shouldn't repeat their story every session
2. Context: Understanding current message requires knowing past conversation
3. Progress tracking: Therapists need to know what's been discussed
4. Personalization: Tailor responses based on user's history

Design decisions:
- Store all messages in database (persistence across sessions)
- Retrieve sliding window of recent messages for context
- Format as chat history for expert models
- Track conversation metrics (session length, topics, etc.)
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from database import Message, User

logger = logging.getLogger(__name__)


# ==================== Conversation Retrieval ====================

async def get_conversation_history(
    db: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[Dict]:
    """
    Retrieve recent conversation history for a user

    This provides context for generating relevant responses.
    The history is returned in chronological order (oldest to newest).

    Args:
        db: Database session
        user_id: User's database ID
        limit: Maximum number of messages to retrieve (default: 10)

    Returns:
        List of message dictionaries with format:
        [
            {'role': 'user', 'content': '...', 'timestamp': datetime, 'expert': 'cbt'},
            {'role': 'assistant', 'content': '...', 'timestamp': datetime, 'expert': 'cbt'},
            ...
        ]

    Why limit to 10 messages?
    - Balance between context and performance
    - ~5 exchanges (user + assistant pairs)
    - Most relevant context is recent
    - Prevents token overflow if using LLM APIs

    Example:
        >>> history = await get_conversation_history(db, user_id=1, limit=10)
        >>> for msg in history:
        ...     print(f"{msg['role']}: {msg['content'][:50]}...")
    """

    # Query recent messages for this user, ordered by timestamp descending
    query = (
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(desc(Message.timestamp))
        .limit(limit)
    )

    result = await db.execute(query)
    messages = result.scalars().all()

    # Convert to list of dicts, reverse to get chronological order
    history = [
        {
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.timestamp,
            'expert': msg.expert_used,
        }
        for msg in reversed(messages)
    ]

    logger.info(f"Retrieved {len(history)} messages for user {user_id}")
    return history


async def get_recent_context_summary(
    db: AsyncSession,
    user_id: int,
    window_minutes: int = 60
) -> Dict:
    """
    Get a summary of recent conversation activity

    This provides metadata about the conversation for analytics and routing.

    Args:
        db: Database session
        user_id: User's database ID
        window_minutes: Time window to consider (default: 60 minutes)

    Returns:
        Dict with summary statistics:
        {
            'message_count': int,
            'duration_minutes': float,
            'experts_used': List[str],
            'last_message_time': datetime,
            'session_active': bool,
        }

    Use cases:
    - Detect if user is in an active session
    - Track which experts have been consulted
    - Rate limiting (messages per hour)
    - Session analytics
    """

    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

    # Query messages in the time window
    query = (
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.timestamp >= cutoff_time)
        .order_by(desc(Message.timestamp))
    )

    result = await db.execute(query)
    recent_messages = result.scalars().all()

    if not recent_messages:
        return {
            'message_count': 0,
            'duration_minutes': 0,
            'experts_used': [],
            'last_message_time': None,
            'session_active': False,
        }

    # Calculate statistics
    message_count = len(recent_messages)
    last_message_time = recent_messages[0].timestamp
    first_message_time = recent_messages[-1].timestamp
    duration = (last_message_time - first_message_time).total_seconds() / 60

    # Track which experts were used
    experts_used = list(set(
        msg.expert_used for msg in recent_messages
        if msg.expert_used is not None
    ))

    # Consider session active if last message was within 15 minutes
    session_active = (datetime.utcnow() - last_message_time).total_seconds() < 900

    return {
        'message_count': message_count,
        'duration_minutes': duration,
        'experts_used': experts_used,
        'last_message_time': last_message_time,
        'session_active': session_active,
    }


# ==================== Message Storage ====================

async def save_message(
    db: AsyncSession,
    user_id: int,
    role: str,
    content: str,
    expert_used: Optional[str] = None
) -> Message:
    """
    Save a message to the database

    This stores conversation history for context and audit trail.

    Args:
        db: Database session
        user_id: User's database ID
        role: 'user' or 'assistant'
        content: Message text
        expert_used: Which expert generated this response (for assistant messages)

    Returns:
        Message: The created message object

    Example:
        >>> # Save user message
        >>> user_msg = await save_message(db, user_id=1, role='user', content='I feel anxious')
        >>>
        >>> # Save assistant response
        >>> bot_msg = await save_message(
        ...     db, user_id=1, role='assistant',
        ...     content='Tell me more...', expert_used='cbt'
        ... )
    """

    message = Message(
        user_id=user_id,
        role=role,
        content=content,
        expert_used=expert_used,
        timestamp=datetime.utcnow()
    )

    db.add(message)
    await db.flush()  # Flush to get the message ID without committing

    logger.info(f"Saved {role} message for user {user_id} (expert: {expert_used})")

    return message


# ==================== Context Formatting ====================

def format_conversation_for_context(history: List[Dict], max_chars: int = 2000) -> str:
    """
    Format conversation history as a readable context string

    This converts the message history into a formatted text block
    that can be included in prompts or shown to experts.

    Args:
        history: List of message dicts from get_conversation_history()
        max_chars: Maximum length of formatted output (prevents token overflow)

    Returns:
        str: Formatted conversation history

    Example output:
        '''
        Recent conversation:

        User: I've been feeling really anxious lately
        Assistant (CBT): I hear that you're experiencing anxiety. Can you tell me more about when you notice it most?
        User: Mostly at work when I have to present
        Assistant (CBT): That's a common trigger. Let's explore what thoughts come up before presentations...
        '''
    """

    if not history:
        return "No previous conversation history."

    # Build formatted string
    lines = ["Recent conversation:\n"]

    for msg in history:
        # Format role
        if msg['role'] == 'user':
            role_label = "User"
        else:
            expert = msg.get('expert', 'Unknown')
            role_label = f"Assistant ({expert.upper()})" if expert else "Assistant"

        # Truncate long messages
        content = msg['content']
        if len(content) > 200:
            content = content[:197] + "..."

        lines.append(f"{role_label}: {content}")

    formatted = "\n".join(lines)

    # Truncate if too long
    if len(formatted) > max_chars:
        formatted = formatted[:max_chars - 3] + "..."
        formatted += "\n\n[Earlier messages truncated]"

    return formatted


# ==================== User Session Management ====================

async def get_or_create_user(
    db: AsyncSession,
    user_identifier: str
) -> Tuple[User, bool]:
    """
    Get existing user or create new one

    This ensures every user has a database record for tracking conversations.

    Args:
        db: Database session
        user_identifier: Unique identifier (phone number, username, etc.)

    Returns:
        Tuple of (User object, is_new: bool)
        is_new is True if user was just created

    Example:
        >>> user, is_new = await get_or_create_user(db, "+15551234567")
        >>> if is_new:
        ...     print("Welcome new user!")
        ... else:
        ...     print(f"Welcome back! You've sent {user.message_count} messages")
    """

    # Try to find existing user
    query = select(User).where(User.user_id == user_identifier)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        # Existing user - update last active time
        user.last_active = datetime.utcnow()
        await db.flush()
        logger.info(f"Existing user: {user_identifier} (total messages: {user.message_count})")
        return user, False

    else:
        # New user - create record
        user = User(
            user_id=user_identifier,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            message_count=0,
            is_flagged=False,
        )
        db.add(user)
        await db.flush()
        logger.info(f"New user created: {user_identifier}")
        return user, True


async def increment_message_count(
    db: AsyncSession,
    user_id: int
):
    """
    Increment the user's message count

    This tracks total messages for rate limiting and analytics.

    Args:
        db: Database session
        user_id: User's database ID
    """

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one()

    user.message_count += 1
    await db.flush()


async def check_rate_limit(
    db: AsyncSession,
    user_id: int,
    window_minutes: int = 60,
    max_messages: int = 30
) -> Tuple[bool, int]:
    """
    Check if user has exceeded rate limit

    This prevents abuse and manages system load.

    Args:
        db: Database session
        user_id: User's database ID
        window_minutes: Time window for rate limiting
        max_messages: Maximum messages allowed in window

    Returns:
        Tuple of (is_allowed: bool, remaining_messages: int)

    Example:
        >>> allowed, remaining = await check_rate_limit(db, user_id=1)
        >>> if not allowed:
        ...     return "You've reached the message limit. Please try again later."
    """

    cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

    # Count messages in window
    query = (
        select(func.count(Message.id))
        .where(Message.user_id == user_id)
        .where(Message.role == 'user')  # Only count user messages, not bot responses
        .where(Message.timestamp >= cutoff_time)
    )

    result = await db.execute(query)
    message_count = result.scalar()

    is_allowed = message_count < max_messages
    remaining = max(0, max_messages - message_count)

    if not is_allowed:
        logger.warning(
            f"Rate limit exceeded for user {user_id}: "
            f"{message_count}/{max_messages} messages in {window_minutes} minutes"
        )

    return is_allowed, remaining
