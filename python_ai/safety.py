"""
Crisis Detection and Safety System

**THIS IS THE MOST CRITICAL MODULE FOR A THERAPY BOT**

This module implements safety guardrails to detect and respond to crisis situations.
It uses pattern matching and keyword detection to identify concerning content.

In production, this should be enhanced with:
1. ML-based crisis detection models
2. Integration with human crisis counselors
3. Real-time alerting systems
4. Legal compliance (mandatory reporting for child abuse, etc.)

IMPORTANT ETHICAL CONSIDERATIONS:
- This is a supplemental tool, NOT a replacement for professional care
- Users should always be directed to qualified professionals in crisis
- Privacy vs. safety: In true emergencies, privacy may need to be breached
- Legal obligations vary by jurisdiction (mandatory reporting laws)
"""

import re
import json
import logging
from typing import Tuple, Optional, Dict, List
from datetime import datetime
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)


# ==================== Crisis Types and Severity ====================

class CrisisType(str, Enum):
    """
    Types of crisis situations we detect

    Each type requires different interventions and resources
    """
    SUICIDE = "suicide"  # Suicidal ideation, planning, or intent
    SELF_HARM = "self_harm"  # Non-suicidal self-injury
    HARM_TO_OTHERS = "harm_to_others"  # Violence, threats
    ABUSE = "abuse"  # Disclosures of abuse (child, domestic, elder)
    SUBSTANCE = "substance"  # Dangerous substance use
    MEDICAL = "medical"  # Medical emergencies


class Severity(str, Enum):
    """
    Severity levels for triage and response

    CRITICAL: Immediate intervention required
    HIGH: Urgent intervention needed
    MEDIUM: Concern present, provide resources
    LOW: Minor concern, monitor
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ==================== Crisis Detection Patterns ====================

# These patterns are based on research in crisis detection and mental health NLP
# Sources: Crisis Text Line data, suicide prevention research, clinical guidelines

CRISIS_PATTERNS = {
    CrisisType.SUICIDE: {
        # Patterns indicating suicidal ideation, planning, or intent
        # Sorted by severity (most severe first)
        Severity.CRITICAL: [
            # Imminent intent - immediate danger
            r'\b(going to|gonna|about to)\s+(kill myself|end it|commit suicide|take my life)\b',
            r'\b(tonight|today|right now|soon)\s+.*\b(kill myself|end it|suicide)\b',
            r'\b(goodbye|farewell).*\b(cruel world|everyone|forever)\b',
            r'\b(wrote|writing)\s+(suicide note|goodbye letter)\b',
            r'\bhave\s+(pills|gun|rope|blade).*\b(ready|here|with me)\b',
        ],
        Severity.HIGH: [
            # Clear suicidal ideation with planning
            r'\bwant to\s+(die|kill myself|end (it|my life)|commit suicide)\b',
            r'\b(wish I|should|would rather)\s+(were dead|was dead|didn\'t exist)\b',
            r'\bplan(ning)?\s+to\s+(kill myself|commit suicide|end it)\b',
            r'\bworld.*better.*without me\b',
            r'\bcan\'t go on|don\'t want to live\b',
            r'\bthinking about\s+(suicide|killing myself|ending it)\b',
        ],
        Severity.MEDIUM: [
            # Passive ideation - concerning but less immediate
            r'\blife.*not worth living\b',
            r'\bno reason to (live|be here|continue|go on)\b',
            r'\beveryone.*better off.*without me\b',
            r'\btired of (living|life|existing|being alive)\b',
        ],
    },

    CrisisType.SELF_HARM: {
        Severity.HIGH: [
            r'\b(cutting|burning|hurting)\s+myself\b',
            r'\b(cut|hurt|harm)\s+myself.*\b(again|today|tonight)\b',
            r'\bself(-| )harm\b',
            r'\burge to\s+(cut|hurt|harm)\b',
        ],
        Severity.MEDIUM: [
            r'\bwant to\s+(cut|hurt|harm)\s+myself\b',
            r'\bthinking about\s+(cutting|hurting)\b',
            r'\bdeserve\s+(pain|to hurt|to suffer)\b',
        ],
    },

    CrisisType.HARM_TO_OTHERS: {
        Severity.CRITICAL: [
            r'\b(going to|gonna)\s+(kill|hurt|attack)\s+(him|her|them|someone)\b',
            r'\bhave\s+(gun|weapon|knife).*\b(ready|with me|loaded)\b',
        ],
        Severity.HIGH: [
            r'\bwant to\s+(kill|hurt|harm)\s+(someone|people|them)\b',
            r'\bthey deserve to (die|suffer|pay)\b',
            r'\bplan(ning)?\s+to\s+(kill|hurt|attack)\b',
        ],
        Severity.MEDIUM: [
            r'\bviolent thoughts\b',
            r'\bimagining\s+(hurting|killing|harming)\b',
            r'\bfantasies about\s+(violence|hurting)\b',
        ],
    },

    CrisisType.ABUSE: {
        Severity.HIGH: [
            r'\b(he|she|they).*\b(hits|beats|hurts|touches)\s+me\b',
            r'\b(being|been)\s+(abused|molested|raped|assaulted)\b',
            r'\b(my|the)\s+(dad|mom|parent|husband|wife|partner|boyfriend|girlfriend).*\b(hits|beats|hurts|abuses)\b',
        ],
        Severity.MEDIUM: [
            r'\bafraid of\s+(him|her|them|my\s+(partner|parent))\b',
            r'\bthreaten(s|ed)\s+to\s+(kill|hurt|harm)\s+me\b',
        ],
    },

    CrisisType.SUBSTANCE: {
        Severity.CRITICAL: [
            r'\b(overdosed|overdosing|took too many)\b',
            r'\btook\s+\d+\s+(pills|tablets)\b',
            r'\bmixed\s+(alcohol|drugs)\s+with\b',
        ],
        Severity.HIGH: [
            r'\bcan\'t stop\s+(drinking|using|taking)\b',
            r'\baddicted to\b',
            r'\bwithdrawal\s+(symptoms|shakes)\b',
        ],
    },

    CrisisType.MEDICAL: {
        Severity.CRITICAL: [
            r'\b(chest pain|can\'t breathe|heart attack|stroke)\b',
            r'\b(severe|extreme|unbearable)\s+pain\b',
            r'\bbleeding.*\b(won\'t stop|heavily|severely)\b',
        ],
    },
}


# ==================== Crisis Detection Function ====================

def detect_crisis(message: str) -> Tuple[bool, Optional[Dict]]:
    """
    Analyze a message for crisis indicators

    This function scans the message against all crisis patterns and returns
    the most severe match found.

    Algorithm:
    1. Normalize the message (lowercase, preserve structure)
    2. Check against all patterns in severity order (critical -> low)
    3. Return first match found (highest severity)
    4. If multiple types match, prioritize: suicide > harm_to_others > others

    Args:
        message: User's message text

    Returns:
        Tuple of (is_crisis: bool, crisis_info: Dict or None)

        crisis_info contains:
        {
            'type': CrisisType,
            'severity': Severity,
            'matched_pattern': str,
            'keywords': List[str],
            'timestamp': datetime
        }

    Example:
        >>> detect_crisis("I want to kill myself")
        (True, {
            'type': 'suicide',
            'severity': 'high',
            'matched_pattern': r'\bwant to\s+(die|kill myself|...)',
            'keywords': ['kill myself'],
            'timestamp': datetime(...)
        })
    """

    if not settings.crisis_detection_enabled:
        logger.warning("Crisis detection is DISABLED - this is dangerous in production!")
        return False, None

    # Normalize message for pattern matching
    # Keep original case for some patterns, but make comparison case-insensitive
    normalized = message.lower().strip()

    # Track the most severe crisis found
    most_severe_crisis = None
    highest_severity_level = 0  # Used for comparison (critical=3, high=2, medium=1, low=0)

    severity_priority = {
        Severity.CRITICAL: 3,
        Severity.HIGH: 2,
        Severity.MEDIUM: 1,
        Severity.LOW: 0,
    }

    # Check all crisis patterns
    for crisis_type, severity_patterns in CRISIS_PATTERNS.items():
        for severity, patterns in severity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, normalized, re.IGNORECASE)
                if match:
                    # Found a match - check if it's more severe than previous finds
                    current_severity_level = severity_priority[severity]

                    if current_severity_level > highest_severity_level:
                        highest_severity_level = current_severity_level

                        # Extract matched keywords
                        matched_text = match.group(0)
                        keywords = [matched_text]

                        most_severe_crisis = {
                            'type': crisis_type.value,
                            'severity': severity.value,
                            'matched_pattern': pattern,
                            'keywords': keywords,
                            'timestamp': datetime.utcnow(),
                        }

                        logger.warning(
                            f"CRISIS DETECTED - Type: {crisis_type.value}, "
                            f"Severity: {severity.value}, "
                            f"Matched: '{matched_text}'"
                        )

                        # If we found a CRITICAL crisis, stop searching
                        # This is the highest severity possible
                        if severity == Severity.CRITICAL:
                            return True, most_severe_crisis

    # Return the most severe crisis found (if any)
    if most_severe_crisis:
        return True, most_severe_crisis
    else:
        return False, None


# ==================== Crisis Response Generation ====================

def generate_crisis_response(crisis_info: Dict) -> str:
    """
    Generate appropriate crisis intervention response

    This provides immediate support resources based on the crisis type and severity.

    IMPORTANT: This is NOT treatment - it's a bridge to professional help.

    The response includes:
    1. Validation and empathy
    2. Crisis hotline information
    3. Immediate safety resources
    4. Encouragement to seek professional help

    Args:
        crisis_info: Dictionary from detect_crisis()

    Returns:
        str: Crisis intervention message

    Crisis Response Best Practices:
    - Be direct and clear (crisis moments are not time for ambiguity)
    - Provide specific action steps
    - Include multiple resource options
    - Avoid minimizing language ("it's not that bad")
    - Don't promise things will get better (can feel invalidating)
    - Do express that help is available
    """

    crisis_type = crisis_info['type']
    severity = crisis_info['severity']

    # Base response - validating and urgent
    response = "I'm very concerned about what you've shared. "

    # Type-specific responses
    if crisis_type == CrisisType.SUICIDE.value:
        if severity in [Severity.CRITICAL.value, Severity.HIGH.value]:
            response += (
                "**This is a crisis situation that requires immediate professional support.**\n\n"
                f"**Please contact the 988 Suicide & Crisis Lifeline:**\n"
                f"- Call or text **{settings.crisis_hotline}** (24/7, free, confidential)\n"
                f"- Chat online: https://988lifeline.org/chat/\n\n"
                "**If you're in immediate danger:**\n"
                "- Call 911 or go to your nearest emergency room\n"
                "- Don't stay alone - reach out to someone you trust\n\n"
                "You deserve support, and these professionals are trained to help. "
                "I'm a chatbot and can't provide the level of care you need right now, "
                "but real people who care are available 24/7 at the numbers above."
            )
        else:  # MEDIUM severity
            response += (
                "It sounds like you're going through a really difficult time. "
                "While I'm here to listen, I want you to know about resources that can provide more support:\n\n"
                f"**988 Suicide & Crisis Lifeline:** Call/text **{settings.crisis_hotline}** anytime (24/7, free)\n\n"
                "These counselors are trained to help with thoughts of suicide and can provide support. "
                "Would you like to talk about what's been going on?"
            )

    elif crisis_type == CrisisType.SELF_HARM.value:
        response += (
            "Self-harm is a sign of serious distress, and you deserve support.\n\n"
            f"**Crisis resources:**\n"
            f"- 988 Suicide & Crisis Lifeline: **{settings.crisis_hotline}** (24/7)\n"
            "- Crisis Text Line: Text HOME to 741741\n\n"
            "**Immediate coping strategies:**\n"
            "- Hold ice in your hand\n"
            "- Snap a rubber band on your wrist\n"
            "- Draw on your skin with red marker\n\n"
            "Please reach out to a mental health professional who can help address "
            "what's causing this urge."
        )

    elif crisis_type == CrisisType.HARM_TO_OTHERS.value:
        response += (
            "Thoughts of harming others are a serious concern. Please seek immediate help.\n\n"
            f"**Crisis resources:**\n"
            f"- 988 Suicide & Crisis Lifeline: **{settings.crisis_hotline}**\n"
            "- Go to your nearest emergency room\n"
            "- Call 911 if anyone is in immediate danger\n\n"
            "A mental health professional can help you work through these thoughts safely."
        )

    elif crisis_type == CrisisType.ABUSE.value:
        response += (
            "I'm sorry you're experiencing this. Abuse is never okay, and you deserve safety and support.\n\n"
            "**Resources:**\n"
            "- National Domestic Violence Hotline: 1-800-799-7233 (24/7)\n"
            "- Crisis Text Line: Text HOME to 741741\n"
            f"- {settings.crisis_hotline} for emotional support\n\n"
            "These services can help you:\n"
            "- Safety planning\n"
            "- Connect with local resources\n"
            "- Understand your options\n\n"
            "You don't have to face this alone."
        )

    elif crisis_type == CrisisType.SUBSTANCE.value:
        if severity == Severity.CRITICAL.value:
            response += (
                "**This is a medical emergency. Please:**\n"
                "- Call 911 immediately\n"
                "- Don't stay alone\n"
                "- Don't delay getting help\n\n"
                "Overdoses and dangerous substance combinations need immediate medical attention."
            )
        else:
            response += (
                "Substance use concerns deserve professional support.\n\n"
                "**Resources:**\n"
                "- SAMHSA National Helpline: 1-800-662-4357 (24/7, free)\n"
                f"- Crisis support: {settings.crisis_hotline}\n\n"
                "These services can connect you with treatment options and support."
            )

    elif crisis_type == CrisisType.MEDICAL.value:
        response += (
            "**This sounds like a medical emergency.**\n\n"
            "**Please call 911 or go to your nearest emergency room immediately.**\n\n"
            "Don't wait - medical emergencies require immediate professional care. "
            "I'm a chatbot and cannot provide medical assistance."
        )

    # Add general footer
    response += "\n\n---\n"
    response += (
        "*I'm an AI chatbot designed to provide supportive conversations, "
        "but I'm not a substitute for professional mental health care or emergency services. "
        "Please use the resources above to get the help you deserve.*"
    )

    return response


# ==================== Safety Check Summary ====================

def get_safety_summary() -> str:
    """
    Get a summary of the safety system configuration

    Useful for startup logging and diagnostics

    Returns:
        str: Multi-line summary of safety configuration
    """
    summary = "=== Safety System Configuration ===\n"
    summary += f"Crisis Detection: {'ENABLED' if settings.crisis_detection_enabled else 'DISABLED ⚠️'}\n"
    summary += f"Crisis Hotline: {settings.crisis_hotline}\n"
    summary += f"Crisis Alerts: {'Enabled' if settings.crisis_alert_email else 'Disabled'}\n"

    # Count patterns
    total_patterns = 0
    for crisis_type, severity_patterns in CRISIS_PATTERNS.items():
        for severity, patterns in severity_patterns.items():
            total_patterns += len(patterns)

    summary += f"Detection Patterns: {total_patterns} across {len(CRISIS_PATTERNS)} crisis types\n"
    summary += "==================================="

    return summary
