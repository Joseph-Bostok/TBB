"""
Database Models and Session Management

This module defines the database schema using SQLAlchemy ORM.
It includes models for users, messages, and safety incidents.

Key Design Decisions:
1. Async SQLAlchemy for non-blocking I/O
2. Separate tables for messages and safety incidents (normalized design)
3. Indexes on frequently queried fields (user_id, timestamp)
4. Safety-first approach with incident tracking
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Boolean, Integer, Float, ForeignKey, Index, JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import json

from config import settings

logger = logging.getLogger(__name__)


# ==================== Base Model ====================
class Base(DeclarativeBase):
    """
    Base class for all database models

    All models inherit from this class to get SQLAlchemy ORM functionality
    """
    pass


# ==================== User Model ====================
class User(Base):
    """
    User Model

    Stores user information and preferences.
    In a production SMS bot, user_id would be the phone number (hashed for privacy).

    Fields:
    - user_id: Unique identifier (phone number hash or user ID)
    - created_at: Account creation timestamp
    - last_active: Last interaction timestamp (for dormancy detection)
    - message_count: Total messages sent (for rate limiting)
    - is_flagged: Whether user has triggered crisis detection
    - preferred_expert: If user has a preference for CBT/mindfulness/motivation
    """
    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # User identifier (phone number in production, username in demo)
    # Indexed for fast lookup
    user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Usage metrics
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Safety flags
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Preferences
    preferred_expert: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Communication style learning
    communication_style: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON storing style metrics

    # Relationships
    # One user has many messages
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    # One user can have many safety incidents
    safety_incidents: Mapped[List["SafetyIncident"]] = relationship("SafetyIncident", back_populates="user", cascade="all, delete-orphan")

    # One user has many important events
    important_events: Mapped[List["ImportantEvent"]] = relationship("ImportantEvent", back_populates="user", cascade="all, delete-orphan")

    # One user has many scheduled messages
    scheduled_messages: Mapped[List["ScheduledMessage"]] = relationship("ScheduledMessage", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', messages={self.message_count}, flagged={self.is_flagged})>"


# ==================== Message Model ====================
class Message(Base):
    """
    Message Model

    Stores conversation history for context and memory.
    Each message has a role (user or assistant) and is linked to an expert.

    Why store messages?
    1. Conversation context for better responses
    2. Audit trail for safety review
    3. Analytics and improvement
    4. User history for continuity

    Fields:
    - user_id: Foreign key to User
    - role: 'user' or 'assistant'
    - content: Message text
    - expert_used: Which expert handled this (CBT, mindfulness, motivation)
    - timestamp: When the message was sent
    """
    __tablename__ = "messages"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to users table
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Message metadata
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    expert_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'cbt', 'mindfulness', 'motivation'
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship back to user
    user: Mapped["User"] = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<Message(user_id={self.user_id}, role='{self.role}', expert='{self.expert_used}')>"


# Composite index for efficient queries: "Get recent messages for user X"
Index('idx_user_timestamp', Message.user_id, Message.timestamp.desc())


# ==================== Safety Incident Model ====================
class SafetyIncident(Base):
    """
    Safety Incident Model

    **CRITICAL FOR THERAPY APPLICATIONS**

    Tracks when the crisis detection system identifies concerning content.
    This enables:
    1. Immediate intervention (show crisis resources)
    2. Audit trail for legal/medical review
    3. Pattern detection (escalating risk)
    4. Quality improvement

    Incident Types:
    - suicide: Suicidal ideation or intent
    - self_harm: Non-suicidal self-injury
    - harm_to_others: Threats or violence
    - abuse: Disclosures of abuse (child, domestic, elder)
    - substance: Dangerous substance use

    Fields:
    - user_id: Who triggered the incident
    - message_id: Which message triggered it
    - incident_type: Category of crisis
    - severity: low/medium/high/critical
    - detected_keywords: What patterns were matched
    - action_taken: What intervention occurred
    - resolved: Whether follow-up occurred
    """
    __tablename__ = "safety_incidents"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)

    # Incident details
    incident_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'suicide', 'self_harm', 'harm_to_others', etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    detected_keywords: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array of matched patterns

    # Response tracking
    action_taken: Mapped[str] = mapped_column(Text, nullable=True)  # What intervention was provided
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="safety_incidents")

    def __repr__(self):
        return f"<SafetyIncident(type='{self.incident_type}', severity='{self.severity}', resolved={self.resolved})>"


# ==================== Important Event Model ====================
class ImportantEvent(Base):
    """
    Important Event Model

    Tracks important events mentioned by users (tests, appointments, deadlines, etc.)
    This enables proactive follow-up and context-aware support.

    Use Cases:
    - User mentions: "I have a test on Friday"
    - Bot creates event and follows up daily
    - User mentions: "My therapy appointment is next week"
    - Bot checks in before and after

    Fields:
    - user_id: Who mentioned the event
    - event_type: Category (test, appointment, deadline, social, other)
    - description: What the event is
    - event_date: When it occurs
    - importance: User-assigned or inferred (low/medium/high)
    - follow_up_before_days: Days before to check in (e.g., 1, 2, 3)
    - follow_up_after_days: Days after to check in (e.g., 1)
    - completed: Whether the event has passed and been followed up on
    """
    __tablename__ = "important_events"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'test', 'appointment', 'deadline', etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)  # "Math exam", "Therapy appointment"
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    importance: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # 'low', 'medium', 'high'

    # Follow-up configuration
    follow_up_before_days: Mapped[str] = mapped_column(String(100), default="1", nullable=True)  # Comma-separated: "1,2,3"
    follow_up_after_days: Mapped[str] = mapped_column(String(100), default="1", nullable=True)  # Comma-separated: "1"

    # Status
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="important_events")

    def __repr__(self):
        return f"<ImportantEvent(type='{self.event_type}', date='{self.event_date}', completed={self.completed})>"


# ==================== Scheduled Message Model ====================
class ScheduledMessage(Base):
    """
    Scheduled Message Model

    Stores messages to be sent at specific times for proactive outreach.
    This enables the bot to:
    - Follow up on important events
    - Check in daily/weekly
    - Send reminders
    - Provide motivational messages

    Message Types:
    - follow_up: Following up on a mentioned event
    - check_in: Regular wellness check
    - reminder: Reminder for medication, habits, etc.
    - motivation: Proactive encouragement

    Fields:
    - user_id: Recipient
    - message_content: What to send
    - scheduled_time: When to send it
    - message_type: Category of message
    - related_event_id: If following up on an event
    - sent: Whether it's been delivered
    - sent_at: When it was actually sent
    """
    __tablename__ = "scheduled_messages"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    related_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("important_events.id"), nullable=True)

    # Message details
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'follow_up', 'check_in', 'reminder'

    # Scheduling
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="scheduled_messages")

    def __repr__(self):
        return f"<ScheduledMessage(type='{self.message_type}', scheduled='{self.scheduled_time}', sent={self.sent})>"


# Index for efficient scheduling queries
Index('idx_scheduled_unsent', ScheduledMessage.scheduled_time, ScheduledMessage.sent)


# ==================== Database Engine and Session ====================

# Create async engine
# echo=True would log all SQL queries (useful for debugging)
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL in development only
    future=True
)

# Create async session factory
# expire_on_commit=False prevents objects from being expired after commit
# This is useful for accessing relationships after commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


# ==================== Database Utilities ====================

async def init_db():
    """
    Initialize database tables

    This creates all tables defined in the Base class.
    Should be called on application startup.

    In production, use Alembic for migrations instead:
    - alembic init alembic
    - alembic revision --autogenerate -m "Initial migration"
    - alembic upgrade head
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI endpoints

    Provides a database session that automatically closes after use.

    Usage in FastAPI:
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        return result.scalars().all()

    The session is automatically committed or rolled back based on success/failure.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """
    Close database connections

    Should be called on application shutdown to cleanly close connections.
    """
    await engine.dispose()
    logger.info("Database connections closed")
