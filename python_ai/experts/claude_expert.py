"""
Claude-Powered Expert

This expert uses Anthropic's Claude API for truly conversational,
empathetic responses that feel human and build real relationships.

Claude is particularly good at:
- Empathy and emotional intelligence
- Therapeutic conversations
- Maintaining context over long conversations
- Adapting tone and style
- ADHD and mental health support
"""

import logging
from typing import List, Dict, Optional
from anthropic import Anthropic
from config import settings

logger = logging.getLogger(__name__)


class ClaudeExpert:
    """
    Uses Claude API for conversational therapy responses

    This expert provides fully conversational, context-aware responses
    that adapt to the user's needs and build a therapeutic relationship.
    """

    def __init__(self):
        """Initialize Claude client"""
        self.client = None
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

        if settings.anthropic_api_key:
            try:
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Claude expert initialized with API key")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.client = None
        else:
            logger.warning("No Anthropic API key provided - Claude expert will use fallback responses")

    def is_available(self) -> bool:
        """Check if Claude API is available"""
        return self.client is not None

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Dict = None
    ) -> str:
        """
        Generate therapeutic response using Claude

        Args:
            user_message: Current message from user
            conversation_history: Previous conversation
            context: Additional context (routing info, etc.)

        Returns:
            Therapeutic response from Claude
        """

        if not self.is_available():
            return self._fallback_response(user_message, context)

        try:
            # Build conversation for Claude
            messages = self._build_messages(user_message, conversation_history)

            # System prompt for therapeutic context
            system_prompt = self._build_system_prompt(context)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            # Extract response text
            response_text = response.content[0].text

            logger.info(f"Claude generated response ({len(response_text)} chars)")
            return response_text

        except Exception as e:
            logger.error(f"Claude API error: {e}", exc_info=True)
            return self._fallback_response(user_message, context)

    def _build_system_prompt(self, context: Dict = None) -> str:
        """
        Build system prompt for Claude

        This defines Claude's role, style, and approach.
        """

        prompt = """You are a supportive AI therapy assistant designed to help people with ADHD, anxiety, depression, and other mental health challenges.

Your role:
- Provide empathetic, non-judgmental support
- Use evidence-based therapeutic techniques (CBT, mindfulness, motivation)
- Help users track important events and provide proactive follow-ups
- Adapt your communication style to match the user
- Build a genuine, supportive relationship over time

Guidelines:
- Be warm, human, and conversational (not clinical)
- Use simple language, not therapy jargon
- Keep responses concise but meaningful
- Ask follow-up questions to show you care
- Remember context from previous messages
- Provide practical, actionable suggestions
- Validate emotions before offering solutions
- For ADHD: Break tasks down, offer structure, normalize struggles

Important safety notes:
- You are a support tool, NOT a replacement for professional therapy
- If crisis detected (already handled), provide 988 hotline
- Encourage professional help for serious concerns
- Never diagnose or prescribe medication

Communication style:
- Text message format (brief, natural)
- Match user's formality level
- Be supportive but not overly cheerful
- Show consistency to build trust"""

        # Add context-specific guidance
        if context:
            expert_type = context.get('expert', 'general')
            if expert_type == 'cbt':
                prompt += "\n\nFocus: Helping with anxiety, depression, negative thought patterns (CBT techniques)"
            elif expert_type == 'mindfulness':
                prompt += "\n\nFocus: Stress management, sleep issues, relaxation techniques"
            elif expert_type == 'motivation':
                prompt += "\n\nFocus: ADHD support, procrastination, motivation, goal-setting"

        return prompt

    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Dict]
    ) -> List[Dict]:
        """
        Build message list for Claude API

        Formats conversation history into Claude's message format.
        """

        messages = []

        # Add recent conversation history (last 10 messages)
        for msg in conversation_history[-10:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

    def _fallback_response(
        self,
        user_message: str,
        context: Dict = None
    ) -> str:
        """
        Fallback response when Claude API unavailable

        Provides helpful response even without API access.
        """

        expert_type = context.get('expert', 'general') if context else 'general'

        responses = {
            'cbt': "I hear you're dealing with some difficult thoughts or feelings. While I'm having trouble connecting to my full capabilities right now, I want you to know that what you're experiencing is valid. Can you tell me more about what's been on your mind?",

            'mindfulness': "It sounds like you're feeling stressed or having trouble relaxing. Even though I'm in limited mode right now, I can suggest: try taking 3 deep breaths, focusing on each exhale. Sometimes just pausing helps. What's been causing the most stress?",

            'motivation': "I understand you're struggling with focus or motivation - that's really common, especially with ADHD. While I'm in limited mode, here's a quick tip: try setting a 5-minute timer and just starting. Sometimes that's enough to build momentum. What are you trying to work on?"
        }

        return responses.get(expert_type,
            "I'm here to support you, though I'm currently in limited mode. I'm listening and want to help. Can you tell me more about what's going on?")


# Global Claude expert instance
_claude_expert = None

def get_claude_expert() -> ClaudeExpert:
    """
    Get global Claude expert instance (singleton pattern)

    Returns:
        ClaudeExpert instance
    """
    global _claude_expert
    if _claude_expert is None:
        _claude_expert = ClaudeExpert()
    return _claude_expert
