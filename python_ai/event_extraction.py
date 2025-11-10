"""
Event Extraction Module

Detects and extracts important events from user messages for proactive follow-up.

This module identifies when users mention:
- Tests and exams
- Appointments (therapy, doctor, etc.)
- Deadlines (work, school, personal)
- Important dates (interviews, presentations)
- Social events that cause anxiety

Example extractions:
- "I have a test on Friday" -> Event(type='test', date=<next Friday>, desc='test')
- "My therapy appointment is next week" -> Event(type='appointment', date=<next week>)
- "Need to finish my project by Monday" -> Event(type='deadline', date=<next Monday>)
"""

from typing import Optional, List, Tuple, Dict
import re
from datetime import datetime, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import ImportantEvent, User

logger = logging.getLogger(__name__)


class EventExtractor:
    """
    Extracts important events from user messages

    Uses pattern matching and date parsing to identify events
    and their associated dates.
    """

    def __init__(self):
        # Event type patterns
        self.event_patterns = {
            "test": [
                r'\b(test|exam|quiz|midterm|final)\b',
                r'\b(testing|examination)\b',
            ],
            "appointment": [
                r'\b(appointment|meeting|session)\b',
                r'\b(doctor|therapist|therapy|counseling)\b',
                r'\b(see (my )?(doctor|therapist))\b',
            ],
            "deadline": [
                r'\b(deadline|due date|submit|turn in)\b',
                r'\b(project due|assignment due|paper due)\b',
                r'\b(need to finish|have to complete)\b',
            ],
            "interview": [
                r'\b(interview|job interview)\b',
            ],
            "presentation": [
                r'\b(presentation|present|presenting)\b',
            ],
            "social": [
                r'\b(party|event|gathering|meetup)\b',
                r'\b(date|dinner|lunch with)\b',
            ],
        }

        # Date patterns (relative and absolute)
        self.date_patterns = {
            "today": r'\btoday\b',
            "tomorrow": r'\btomorrow\b',
            "this_week": r'\bthis week\b',
            "next_week": r'\bnext week\b',
            "monday": r'\b(this |next )?monday\b',
            "tuesday": r'\b(this |next )?tuesday\b',
            "wednesday": r'\b(this |next )?wednesday\b',
            "thursday": r'\b(this |next )?thursday\b',
            "friday": r'\b(this |next )?friday\b',
            "saturday": r'\b(this |next )?saturday\b',
            "sunday": r'\b(this |next )?sunday\b',
            "in_n_days": r'\bin (\d+) days?\b',
            "n_days_from_now": r'\b(\d+) days? from now\b',
        }

    def extract_events(self, message: str) -> List[Dict]:
        """
        Extract all events mentioned in a message

        Args:
            message: User's message text

        Returns:
            List of event dictionaries with type, description, and date
        """

        events = []
        message_lower = message.lower()

        # Check for each event type
        for event_type, patterns in self.event_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Found an event, now extract the date
                    date = self._extract_date(message_lower)

                    if date:
                        # Extract description (the part mentioning the event)
                        description = self._extract_description(message, event_type)

                        events.append({
                            "type": event_type,
                            "description": description,
                            "date": date,
                            "importance": self._infer_importance(event_type, message_lower),
                        })
                        break  # Only match once per event type

        return events

    def _extract_date(self, message: str) -> Optional[datetime]:
        """
        Extract date from message

        Args:
            message: Message text (lowercase)

        Returns:
            datetime object or None
        """

        now = datetime.now()

        # Check for "today"
        if re.search(self.date_patterns["today"], message):
            return now.replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for "tomorrow"
        if re.search(self.date_patterns["tomorrow"], message):
            return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for "this week" - assume Friday of this week
        if re.search(self.date_patterns["this_week"], message):
            days_until_friday = (4 - now.weekday()) % 7
            return (now + timedelta(days=days_until_friday)).replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for "next week" - assume Monday of next week
        if re.search(self.date_patterns["next_week"], message):
            days_until_next_monday = (7 - now.weekday()) % 7 + 7
            return (now + timedelta(days=days_until_next_monday)).replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for specific weekdays
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        for day_name, day_num in weekdays.items():
            match = re.search(self.date_patterns[day_name], message)
            if match:
                # Check if it's "next" day
                is_next = "next" in match.group()

                current_day = now.weekday()
                days_ahead = day_num - current_day

                if days_ahead <= 0 or is_next:
                    # Next occurrence
                    days_ahead += 7

                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for "in N days"
        match = re.search(self.date_patterns["in_n_days"], message)
        if match:
            n_days = int(match.group(1))
            return (now + timedelta(days=n_days)).replace(hour=12, minute=0, second=0, microsecond=0)

        # Check for "N days from now"
        match = re.search(self.date_patterns["n_days_from_now"], message)
        if match:
            n_days = int(match.group(1))
            return (now + timedelta(days=n_days)).replace(hour=12, minute=0, second=0, microsecond=0)

        return None

    def _extract_description(self, message: str, event_type: str) -> str:
        """
        Extract a concise description of the event

        Args:
            message: Original message
            event_type: Type of event detected

        Returns:
            Short description string
        """

        # Try to extract the relevant sentence
        sentences = message.split(".")
        for sentence in sentences:
            if any(pattern for pattern_list in [self.event_patterns[event_type]]
                   for pattern in pattern_list
                   if re.search(pattern, sentence.lower())):
                return sentence.strip()[:100]  # Max 100 chars

        # Fallback to event type
        return f"{event_type.title()}"

    def _infer_importance(self, event_type: str, message: str) -> str:
        """
        Infer importance level of the event

        Args:
            event_type: Type of event
            message: Message text

        Returns:
            Importance level: 'low', 'medium', 'high'
        """

        # High importance indicators
        high_indicators = [
            "important", "crucial", "critical", "must", "have to",
            "really worried", "stressed about", "anxious about"
        ]

        # Low importance indicators
        low_indicators = [
            "maybe", "might", "possibly", "optional", "if i can"
        ]

        message_lower = message.lower()

        if any(indicator in message_lower for indicator in high_indicators):
            return "high"
        elif any(indicator in message_lower for indicator in low_indicators):
            return "low"
        else:
            # Default importance based on event type
            if event_type in ["test", "exam", "interview", "deadline"]:
                return "high"
            elif event_type in ["appointment"]:
                return "medium"
            else:
                return "low"

    async def save_event(
        self,
        db: AsyncSession,
        user_id: int,
        event: Dict
    ) -> Optional[ImportantEvent]:
        """
        Save extracted event to database

        Args:
            db: Database session
            user_id: User ID
            event: Event dictionary from extract_events()

        Returns:
            Created ImportantEvent or None
        """

        try:
            # Determine follow-up schedule based on importance
            if event["importance"] == "high":
                follow_up_before = "1,2,3"  # 3, 2, 1 days before
                follow_up_after = "1,3"  # 1 and 3 days after
            elif event["importance"] == "medium":
                follow_up_before = "1"  # 1 day before
                follow_up_after = "1"  # 1 day after
            else:
                follow_up_before = "1"  # 1 day before
                follow_up_after = ""  # No follow-up after

            db_event = ImportantEvent(
                user_id=user_id,
                event_type=event["type"],
                description=event["description"],
                event_date=event["date"],
                importance=event["importance"],
                follow_up_before_days=follow_up_before,
                follow_up_after_days=follow_up_after,
            )

            db.add(db_event)
            await db.commit()

            logger.info(
                f"Saved event for user {user_id}: {event['type']} on {event['date']} "
                f"(importance: {event['importance']})"
            )

            return db_event

        except Exception as e:
            logger.error(f"Error saving event: {e}", exc_info=True)
            await db.rollback()
            return None

    async def get_upcoming_events(
        self,
        db: AsyncSession,
        user_id: int,
        days_ahead: int = 7
    ) -> List[ImportantEvent]:
        """
        Get user's upcoming events

        Args:
            db: Database session
            user_id: User ID
            days_ahead: How many days ahead to look

        Returns:
            List of ImportantEvent objects
        """

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        query = (
            select(ImportantEvent)
            .where(ImportantEvent.user_id == user_id)
            .where(ImportantEvent.event_date <= cutoff_date)
            .where(ImportantEvent.event_date >= datetime.now())
            .where(ImportantEvent.completed == False)
            .order_by(ImportantEvent.event_date)
        )

        result = await db.execute(query)
        return result.scalars().all()


# Global event extractor instance
_event_extractor = None

def get_event_extractor() -> EventExtractor:
    """
    Get global event extractor instance

    Returns:
        EventExtractor instance
    """
    global _event_extractor
    if _event_extractor is None:
        _event_extractor = EventExtractor()
    return _event_extractor
