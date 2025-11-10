"""
Personalization Module

This module learns and adapts to each user's communication style to provide
more natural, human-like responses that feel personalized.

Key Features:
1. Communication style analysis (formality, emoji usage, length, etc.)
2. Response adaptation based on user preferences
3. Learning from conversation history
4. Natural language mimicry

Design Philosophy:
- Subtle personalization, not mimicry
- Maintain therapeutic boundaries
- Preserve safety and professionalism
- Gradual learning over time
"""

from typing import Dict, List, Optional, Tuple
import json
import re
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import User, Message
from config import settings

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    Learns and adapts to user's communication style

    Analyzes:
    - Message length preferences
    - Formality level
    - Emoji usage
    - Response timing preferences
    - Tone (casual vs formal)
    """

    def __init__(self):
        self.default_style = {
            "avg_message_length": 50,
            "uses_emojis": False,
            "formality": "neutral",  # casual, neutral, formal
            "preferred_greeting": "Hi",
            "tone": "supportive",  # supportive, encouraging, reflective
            "likes_questions": True,
            "prefers_short_responses": False,
        }

    async def analyze_user_style(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = None
    ) -> Dict:
        """
        Analyze user's communication style from message history

        Args:
            db: Database session
            user_id: User to analyze
            limit: Number of recent messages to analyze

        Returns:
            Dictionary with style metrics
        """

        if limit is None:
            limit = settings.style_learning_window

        # Get user's messages only (not assistant responses)
        query = (
            select(Message)
            .where(Message.user_id == user_id)
            .where(Message.role == "user")
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        messages = result.scalars().all()

        if not messages:
            logger.info(f"No messages found for user {user_id}, using default style")
            return self.default_style

        # Analyze messages
        style = self._analyze_messages([msg.content for msg in messages])

        logger.info(f"Analyzed style for user {user_id}: {style}")
        return style

    def _analyze_messages(self, messages: List[str]) -> Dict:
        """
        Analyze list of messages for style patterns

        Args:
            messages: List of message contents

        Returns:
            Style metrics dictionary
        """

        if not messages:
            return self.default_style.copy()

        # Calculate message statistics
        lengths = [len(msg) for msg in messages]
        avg_length = sum(lengths) / len(lengths)

        # Count emoji usage
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)

        emoji_count = sum(1 for msg in messages if emoji_pattern.search(msg))
        uses_emojis = emoji_count > len(messages) * 0.2  # More than 20% of messages

        # Detect formality
        formal_indicators = ["please", "thank you", "appreciate", "grateful"]
        casual_indicators = ["lol", "haha", "yeah", "gonna", "wanna", "hey"]

        formal_count = sum(
            1 for msg in messages
            for indicator in formal_indicators
            if indicator in msg.lower()
        )
        casual_count = sum(
            1 for msg in messages
            for indicator in casual_indicators
            if indicator in msg.lower()
        )

        if formal_count > casual_count * 1.5:
            formality = "formal"
        elif casual_count > formal_count * 1.5:
            formality = "casual"
        else:
            formality = "neutral"

        # Detect greeting style
        greeting_patterns = {
            "Hi": ["hi ", "hi!", "hi,"],
            "Hey": ["hey ", "hey!", "hey,"],
            "Hello": ["hello ", "hello!", "hello,"],
        }

        greeting_counts = {
            greeting: sum(
                1 for msg in messages
                for pattern in patterns
                if msg.lower().startswith(pattern)
            )
            for greeting, patterns in greeting_patterns.items()
        }

        preferred_greeting = max(greeting_counts, key=greeting_counts.get) if any(greeting_counts.values()) else "Hi"

        # Detect if user likes questions (asks many questions)
        question_count = sum(1 for msg in messages if "?" in msg)
        likes_questions = question_count > len(messages) * 0.3

        # Short vs long responses
        prefers_short = avg_length < 30

        return {
            "avg_message_length": round(avg_length, 1),
            "uses_emojis": uses_emojis,
            "formality": formality,
            "preferred_greeting": preferred_greeting,
            "tone": "supportive",  # Can be refined with sentiment analysis
            "likes_questions": likes_questions,
            "prefers_short_responses": prefers_short,
            "message_count_analyzed": len(messages),
            "last_updated": datetime.utcnow().isoformat(),
        }

    async def save_user_style(
        self,
        db: AsyncSession,
        user_id: int,
        style: Dict
    ):
        """
        Save analyzed style to user record

        Args:
            db: Database session
            user_id: User ID
            style: Style dictionary to save
        """

        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            user.communication_style = json.dumps(style)
            await db.commit()
            logger.info(f"Saved communication style for user {user_id}")

    async def get_user_style(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict:
        """
        Retrieve user's saved communication style

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Style dictionary (or default if not found)
        """

        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user and user.communication_style:
            try:
                return json.loads(user.communication_style)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse communication style for user {user_id}")
                return self.default_style.copy()

        return self.default_style.copy()

    def adapt_response(
        self,
        response: str,
        user_style: Dict
    ) -> str:
        """
        Adapt bot response to match user's communication style

        Args:
            response: Original bot response
            user_style: User's communication style

        Returns:
            Adapted response
        """

        adapted = response

        # Adjust greeting
        if response.startswith("Hi ") or response.startswith("Hello "):
            preferred = user_style.get("preferred_greeting", "Hi")
            adapted = re.sub(r"^(Hi|Hello)\s", f"{preferred} ", adapted)

        # Adjust length for users who prefer short responses
        if user_style.get("prefers_short_responses", False) and len(adapted) > 150:
            # Keep only first 1-2 sentences
            sentences = adapted.split(". ")
            if len(sentences) > 2:
                adapted = ". ".join(sentences[:2]) + "."

        # Adjust formality
        formality = user_style.get("formality", "neutral")
        if formality == "casual":
            # Make response more casual
            adapted = adapted.replace("I would", "I'd")
            adapted = adapted.replace("You are", "You're")
            adapted = adapted.replace("I am", "I'm")
        elif formality == "formal":
            # Make response more formal (expand contractions)
            adapted = adapted.replace("I'm", "I am")
            adapted = adapted.replace("you're", "you are")
            adapted = adapted.replace("I'd", "I would")

        return adapted


# Global personalization engine instance
_personalization_engine = None

def get_personalization_engine() -> PersonalizationEngine:
    """
    Get global personalization engine instance

    Returns:
        PersonalizationEngine instance
    """
    global _personalization_engine
    if _personalization_engine is None:
        _personalization_engine = PersonalizationEngine()
    return _personalization_engine
