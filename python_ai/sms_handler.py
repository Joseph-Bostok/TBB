"""
SMS Handler Module with Twilio Integration

This module manages SMS communication with users via Twilio.
It handles:
1. Receiving SMS messages (webhook endpoint)
2. Sending SMS messages (outbound)
3. Phone number validation
4. Message formatting for SMS constraints

SMS Best Practices:
- Keep messages under 160 characters when possible (or split into segments)
- Use clear, concise language
- Provide opt-out instructions
- Handle delivery failures gracefully
"""

from typing import Optional, Tuple
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import settings

logger = logging.getLogger(__name__)


class SMSHandler:
    """
    Manages SMS communication via Twilio

    This class handles all SMS-related operations including:
    - Sending messages to users
    - Validating phone numbers
    - Managing Twilio client connection
    - Error handling and retries
    """

    def __init__(self):
        """Initialize Twilio client if credentials are provided"""
        self.client = None
        self.from_number = settings.twilio_phone_number

        if settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                self.client = Client(
                    settings.twilio_account_sid,
                    settings.twilio_auth_token
                )
                logger.info(f"Twilio client initialized with number: {self.from_number}")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
        else:
            logger.warning("Twilio credentials not provided - SMS functionality will be disabled")

    def is_enabled(self) -> bool:
        """Check if SMS functionality is available"""
        return self.client is not None and self.from_number is not None

    async def send_sms(self, to_number: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Send an SMS message to a user

        Args:
            to_number: Recipient phone number (E.164 format: +15551234567)
            message: Message content to send

        Returns:
            Tuple of (success: bool, message_sid or error: str)

        Example:
            success, result = await sms_handler.send_sms("+15551234567", "Hello!")
            if success:
                logger.info(f"Message sent with SID: {result}")
            else:
                logger.error(f"Failed to send: {result}")
        """

        if not self.is_enabled():
            logger.warning("SMS sending attempted but Twilio is not configured")
            return False, "SMS service not configured"

        try:
            # Format message for SMS (handle long messages)
            formatted_message = self._format_for_sms(message)

            # Send via Twilio
            message_obj = self.client.messages.create(
                body=formatted_message,
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"SMS sent to {to_number}: SID={message_obj.sid}, status={message_obj.status}")
            return True, message_obj.sid

        except TwilioRestException as e:
            logger.error(f"Twilio error sending to {to_number}: {e.code} - {e.msg}")
            return False, f"Twilio error: {e.msg}"

        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_number}: {e}", exc_info=True)
            return False, f"Error: {str(e)}"

    def _format_for_sms(self, message: str, max_length: int = 1600) -> str:
        """
        Format message for SMS constraints

        SMS messages have character limits:
        - Single message: 160 characters (GSM-7)
        - Concatenated: up to 1600 characters (10 segments)

        Args:
            message: Original message
            max_length: Maximum length (default 1600 = 10 SMS segments)

        Returns:
            Formatted message that fits SMS constraints
        """

        # Truncate if too long
        if len(message) > max_length:
            logger.warning(f"Message truncated from {len(message)} to {max_length} chars")
            message = message[:max_length-3] + "..."

        # Remove markdown formatting that doesn't render well in SMS
        # Replace bold with regular text
        message = message.replace("**", "")
        message = message.replace("__", "")

        # Replace bullet points with dashes
        message = message.replace("• ", "- ")
        message = message.replace("* ", "- ")

        return message.strip()

    @staticmethod
    def normalize_phone_number(phone: str) -> str:
        """
        Normalize phone number to E.164 format

        E.164 is the international phone number format: +[country code][number]
        Example: +15551234567

        Args:
            phone: Phone number in various formats

        Returns:
            Normalized phone number

        Examples:
            "(555) 123-4567" -> "+15551234567"
            "555-123-4567" -> "+15551234567"
            "5551234567" -> "+15551234567"
        """

        # Remove all non-digit characters
        digits = ''.join(c for c in phone if c.isdigit())

        # Add +1 for US numbers if not present
        if not phone.startswith('+'):
            if len(digits) == 10:
                return f"+1{digits}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"+{digits}"

        return phone  # Already in E.164 format

    @staticmethod
    def is_valid_phone_number(phone: str) -> bool:
        """
        Validate phone number format

        Args:
            phone: Phone number to validate

        Returns:
            True if valid E.164 format
        """

        # Basic validation: starts with + and has 10-15 digits
        if not phone.startswith('+'):
            return False

        digits = phone[1:]  # Remove +
        if not digits.isdigit():
            return False

        if len(digits) < 10 or len(digits) > 15:
            return False

        return True


# Global SMS handler instance
_sms_handler = None

def get_sms_handler() -> SMSHandler:
    """
    Get global SMS handler instance (singleton pattern)

    Returns:
        SMSHandler instance
    """
    global _sms_handler
    if _sms_handler is None:
        _sms_handler = SMSHandler()
    return _sms_handler
