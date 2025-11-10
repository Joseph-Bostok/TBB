"""
Proactive Outreach Scheduler

This module manages scheduled messages for proactive follow-ups.
It handles:
1. Creating scheduled messages for event follow-ups
2. Running periodic checks to send due messages
3. Sending messages via SMS

Background Task:
This runs as a background task that checks every minute for messages
that need to be sent. It's more reliable than cron jobs for this use case.
"""

from typing import List, Optional
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import ScheduledMessage, ImportantEvent, User, AsyncSessionLocal
from sms_handler import get_sms_handler
from config import settings

logger = logging.getLogger(__name__)


class ProactiveScheduler:
    """
    Manages proactive message scheduling and delivery

    This scheduler:
    - Creates follow-up messages for important events
    - Checks every minute for due messages
    - Sends messages via SMS
    - Marks messages as sent
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.sms_handler = get_sms_handler()

    def start(self):
        """Start the background scheduler"""

        # Schedule the message check task to run every minute
        self.scheduler.add_job(
            self._check_and_send_messages,
            trigger=IntervalTrigger(minutes=1),
            id="send_scheduled_messages",
            name="Send scheduled messages",
            replace_existing=True,
        )

        # Schedule event follow-up creation (runs daily at 9 AM)
        self.scheduler.add_job(
            self._create_event_followups,
            trigger=IntervalTrigger(hours=24),
            id="create_event_followups",
            name="Create event follow-ups",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Proactive scheduler started")

    def shutdown(self):
        """Stop the scheduler gracefully"""
        self.scheduler.shutdown()
        logger.info("Proactive scheduler stopped")

    async def _check_and_send_messages(self):
        """
        Check for messages that need to be sent and send them

        This runs every minute and sends any messages scheduled for
        the current time or earlier.
        """

        try:
            async with AsyncSessionLocal() as db:
                # Query for unsent messages that are due
                now = datetime.utcnow()

                query = (
                    select(ScheduledMessage, User)
                    .join(User, ScheduledMessage.user_id == User.id)
                    .where(
                        and_(
                            ScheduledMessage.sent == False,
                            ScheduledMessage.scheduled_time <= now
                        )
                    )
                    .limit(10)  # Process max 10 per run to avoid overload
                )

                result = await db.execute(query)
                messages_with_users = result.all()

                if messages_with_users:
                    logger.info(f"Found {len(messages_with_users)} scheduled messages to send")

                for scheduled_msg, user in messages_with_users:
                    await self._send_scheduled_message(db, scheduled_msg, user)

                await db.commit()

        except Exception as e:
            logger.error(f"Error in scheduled message check: {e}", exc_info=True)

    async def _send_scheduled_message(
        self,
        db: AsyncSession,
        scheduled_msg: ScheduledMessage,
        user: User
    ):
        """
        Send a single scheduled message

        Args:
            db: Database session
            scheduled_msg: ScheduledMessage to send
            user: User to send to
        """

        try:
            # Send via SMS if enabled
            if self.sms_handler.is_enabled():
                success, result = await self.sms_handler.send_sms(
                    to_number=user.user_id,  # Assuming user_id is phone number
                    message=scheduled_msg.message_content
                )

                if success:
                    # Mark as sent
                    scheduled_msg.sent = True
                    scheduled_msg.sent_at = datetime.utcnow()

                    logger.info(
                        f"Sent scheduled message {scheduled_msg.id} to user {user.user_id}: "
                        f"SID={result}"
                    )
                else:
                    logger.error(
                        f"Failed to send scheduled message {scheduled_msg.id} to user {user.user_id}: "
                        f"{result}"
                    )
            else:
                # SMS not enabled, just mark as sent (demo mode)
                scheduled_msg.sent = True
                scheduled_msg.sent_at = datetime.utcnow()

                logger.info(
                    f"[DEMO MODE] Would send message to {user.user_id}: "
                    f"{scheduled_msg.message_content[:50]}..."
                )

        except Exception as e:
            logger.error(f"Error sending scheduled message {scheduled_msg.id}: {e}", exc_info=True)

    async def _create_event_followups(self):
        """
        Create follow-up messages for upcoming events

        This runs daily and creates scheduled messages for events
        that need follow-up reminders.
        """

        try:
            async with AsyncSessionLocal() as db:
                # Get all incomplete events in the next 7 days
                now = datetime.utcnow()
                week_from_now = now + timedelta(days=7)

                query = (
                    select(ImportantEvent)
                    .where(
                        and_(
                            ImportantEvent.completed == False,
                            ImportantEvent.event_date >= now,
                            ImportantEvent.event_date <= week_from_now
                        )
                    )
                )

                result = await db.execute(query)
                events = result.scalars().all()

                logger.info(f"Creating follow-ups for {len(events)} upcoming events")

                for event in events:
                    await self._create_followups_for_event(db, event)

                await db.commit()

        except Exception as e:
            logger.error(f"Error creating event follow-ups: {e}", exc_info=True)

    async def _create_followups_for_event(
        self,
        db: AsyncSession,
        event: ImportantEvent
    ):
        """
        Create follow-up messages for a specific event

        Args:
            db: Database session
            event: ImportantEvent to create follow-ups for
        """

        # Parse follow-up days
        before_days = [
            int(d.strip())
            for d in event.follow_up_before_days.split(",")
            if d.strip()
        ] if event.follow_up_before_days else []

        after_days = [
            int(d.strip())
            for d in event.follow_up_after_days.split(",")
            if d.strip()
        ] if event.follow_up_after_days else []

        # Create "before" follow-ups
        for days_before in before_days:
            scheduled_time = event.event_date - timedelta(days=days_before)

            # Only create if in the future
            if scheduled_time > datetime.utcnow():
                # Check if already exists
                existing = await self._check_existing_followup(
                    db, event.id, scheduled_time
                )

                if not existing:
                    message = self._generate_followup_message(
                        event, days_before, is_before=True
                    )

                    scheduled_msg = ScheduledMessage(
                        user_id=event.user_id,
                        related_event_id=event.id,
                        message_content=message,
                        message_type="follow_up",
                        scheduled_time=scheduled_time.replace(hour=9, minute=0, second=0),
                    )

                    db.add(scheduled_msg)
                    logger.debug(f"Created follow-up {days_before} days before event {event.id}")

        # Create "after" follow-ups
        for days_after in after_days:
            scheduled_time = event.event_date + timedelta(days=days_after)

            # Check if already exists
            existing = await self._check_existing_followup(
                db, event.id, scheduled_time
            )

            if not existing:
                message = self._generate_followup_message(
                    event, days_after, is_before=False
                )

                scheduled_msg = ScheduledMessage(
                    user_id=event.user_id,
                    related_event_id=event.id,
                    message_content=message,
                    message_type="follow_up",
                    scheduled_time=scheduled_time.replace(hour=9, minute=0, second=0),
                )

                db.add(scheduled_msg)
                logger.debug(f"Created follow-up {days_after} days after event {event.id}")

    async def _check_existing_followup(
        self,
        db: AsyncSession,
        event_id: int,
        scheduled_time: datetime
    ) -> bool:
        """
        Check if a follow-up already exists for this event and time

        Args:
            db: Database session
            event_id: Event ID
            scheduled_time: Scheduled time to check

        Returns:
            True if follow-up exists
        """

        # Check within 1 hour window
        time_min = scheduled_time - timedelta(hours=1)
        time_max = scheduled_time + timedelta(hours=1)

        query = (
            select(ScheduledMessage)
            .where(
                and_(
                    ScheduledMessage.related_event_id == event_id,
                    ScheduledMessage.scheduled_time >= time_min,
                    ScheduledMessage.scheduled_time <= time_max
                )
            )
        )

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    def _generate_followup_message(
        self,
        event: ImportantEvent,
        days: int,
        is_before: bool
    ) -> str:
        """
        Generate a follow-up message for an event

        Args:
            event: ImportantEvent
            days: Number of days before/after
            is_before: True if before event, False if after

        Returns:
            Message text
        """

        if is_before:
            if days == 1:
                time_phrase = "tomorrow"
            else:
                time_phrase = f"in {days} days"

            messages = {
                "test": f"Hi! Just checking in - your {event.description} is {time_phrase}. How's your preparation going?",
                "exam": f"Hey! Your exam is {time_phrase}. How are you feeling about it?",
                "appointment": f"Reminder: You have your {event.description} {time_phrase}. Is there anything you want to prepare or discuss?",
                "deadline": f"Hi! Your deadline is {time_phrase}. How's progress on {event.description}?",
                "interview": f"Your interview is {time_phrase}! How are you feeling? Need any last-minute tips?",
            }

            return messages.get(
                event.event_type,
                f"Hi! Just a reminder - {event.description} is {time_phrase}. How are you doing with it?"
            )

        else:
            if days == 1:
                time_phrase = "yesterday"
            else:
                time_phrase = f"{days} days ago"

            messages = {
                "test": f"Hey! How did your test go {time_phrase}? I'd love to hear about it!",
                "exam": f"How did your exam go? Hope it went well!",
                "appointment": f"How was your appointment {time_phrase}? Hope everything went okay.",
                "deadline": f"How did {event.description} go? Did you meet the deadline?",
                "interview": f"How was your interview? I'm curious to hear how it went!",
            }

            return messages.get(
                event.event_type,
                f"How did {event.description} go? Hope everything went well!"
            )

    async def create_adhoc_message(
        self,
        db: AsyncSession,
        user_id: int,
        message: str,
        scheduled_time: datetime,
        message_type: str = "check_in"
    ) -> ScheduledMessage:
        """
        Create an ad-hoc scheduled message (not related to an event)

        Args:
            db: Database session
            user_id: User ID
            message: Message content
            scheduled_time: When to send
            message_type: Type of message

        Returns:
            Created ScheduledMessage
        """

        scheduled_msg = ScheduledMessage(
            user_id=user_id,
            message_content=message,
            message_type=message_type,
            scheduled_time=scheduled_time,
        )

        db.add(scheduled_msg)
        await db.commit()

        logger.info(f"Created ad-hoc scheduled message for user {user_id} at {scheduled_time}")

        return scheduled_msg


# Global scheduler instance
_scheduler = None

def get_scheduler() -> ProactiveScheduler:
    """
    Get global scheduler instance

    Returns:
        ProactiveScheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ProactiveScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    scheduler.shutdown()
