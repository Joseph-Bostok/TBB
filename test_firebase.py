"""
Quick test script to verify Firebase initialization
"""
import sys
sys.path.insert(0, '/home/user/TBB/python_ai')

from firebase_auth import firebase_manager

def test_firebase():
    print("=" * 60)
    print("Testing Firebase Initialization")
    print("=" * 60)

    if firebase_manager.initialized:
        print("✅ Firebase initialized successfully!")
        print(f"   Credentials loaded from configured path")
        return True
    else:
        print("❌ Firebase failed to initialize")
        print("   Check firebase-credentials.json and .env configuration")
        return False

if __name__ == "__main__":
    success = test_firebase()
    sys.exit(0 if success else 1)
