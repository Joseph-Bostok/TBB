"""
Firebase Phone Authentication Module

This module handles phone number authentication using Firebase.
It provides functions to verify phone numbers and create authenticated sessions.

Architecture:
- Firebase Admin SDK verifies ID tokens from Firebase client
- Client-side Firebase SDK handles sending verification codes
- This module validates tokens and manages user sessions
"""

import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict
import logging
import os
from config import settings

logger = logging.getLogger(__name__)


class FirebaseAuthManager:
    """
    Manages Firebase authentication for phone numbers.

    Flow:
    1. Client sends phone number to Firebase (client-side SDK)
    2. User receives SMS with verification code
    3. Client verifies code and gets ID token
    4. Server verifies ID token using this class
    5. Server creates/updates user session
    """

    def __init__(self):
        """Initialize Firebase Admin SDK with service account credentials."""
        self.initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        """
        Initialize Firebase Admin SDK.

        This loads credentials from the JSON file specified in settings.
        Only initializes once to avoid duplicate app errors.
        """
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.initialized = True
                return

            # Get credentials path from settings
            cred_path = settings.firebase_credentials_path

            if not cred_path:
                logger.warning("Firebase credentials path not configured")
                return

            # Resolve absolute path
            if not os.path.isabs(cred_path):
                # Assume relative to project root
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                cred_path = os.path.join(project_root, cred_path)

            if not os.path.exists(cred_path):
                logger.error(f"Firebase credentials file not found: {cred_path}")
                return

            # Initialize Firebase with credentials
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

            self.initialized = True
            logger.info(f"Firebase initialized successfully with credentials from {cred_path}")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.initialized = False

    async def verify_id_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify a Firebase ID token and extract user information.

        Args:
            id_token: Firebase ID token from client authentication

        Returns:
            Dict with user info (uid, phone_number) or None if invalid

        Example:
            user_info = await firebase_manager.verify_id_token(token)
            if user_info:
                phone_number = user_info['phone_number']
        """
        if not self.initialized:
            logger.error("Firebase not initialized - cannot verify token")
            return None

        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)

            # Extract user information
            user_info = {
                'uid': decoded_token.get('uid'),
                'phone_number': decoded_token.get('phone_number'),
                'firebase_user_id': decoded_token.get('user_id'),
            }

            logger.info(f"Successfully verified token for phone: {user_info.get('phone_number')}")
            return user_info

        except auth.InvalidIdTokenError:
            logger.error("Invalid Firebase ID token")
            return None
        except auth.ExpiredIdTokenError:
            logger.error("Expired Firebase ID token")
            return None
        except Exception as e:
            logger.error(f"Error verifying ID token: {e}")
            return None

    async def get_user_by_phone(self, phone_number: str) -> Optional[Dict]:
        """
        Get Firebase user information by phone number.

        Args:
            phone_number: Phone number in E.164 format (e.g., +15551234567)

        Returns:
            Dict with user info or None if not found
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None

        try:
            user = auth.get_user_by_phone_number(phone_number)
            return {
                'uid': user.uid,
                'phone_number': user.phone_number,
                'created_at': user.user_metadata.creation_timestamp,
            }
        except auth.UserNotFoundError:
            logger.info(f"No Firebase user found for phone: {phone_number}")
            return None
        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    async def create_custom_token(self, uid: str) -> Optional[str]:
        """
        Create a custom Firebase token for a user.

        Args:
            uid: Firebase user ID

        Returns:
            Custom token string or None if error

        Note: This is useful for server-side authentication flows
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None

        try:
            custom_token = auth.create_custom_token(uid)
            return custom_token.decode('utf-8')
        except Exception as e:
            logger.error(f"Error creating custom token: {e}")
            return None


# Global instance
firebase_manager = FirebaseAuthManager()


async def verify_phone_token(id_token: str) -> Optional[str]:
    """
    Convenience function to verify phone token and return phone number.

    Args:
        id_token: Firebase ID token from client

    Returns:
        Phone number in E.164 format or None if invalid

    Example:
        phone_number = await verify_phone_token(token)
        if phone_number:
            # Create or update user session
            pass
    """
    user_info = await firebase_manager.verify_id_token(id_token)
    if user_info:
        return user_info.get('phone_number')
    return None
