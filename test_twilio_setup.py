#!/usr/bin/env python3
"""
Twilio Setup Verification Script

This script checks if your Twilio SMS bot is properly configured.
Run this before testing to ensure everything is set up correctly.
"""

import os
import sys
from pathlib import Path

# Add python_ai to path
sys.path.insert(0, str(Path(__file__).parent / "python_ai"))

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n" + "="*60)
    print("1. Checking .env configuration...")
    print("="*60)

    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ .env file not found!")
        print("   Create it by copying .env.example")
        return False

    print("✓ .env file exists")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv(env_path)

    required_vars = {
        'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID'),
        'TWILIO_AUTH_TOKEN': os.getenv('TWILIO_AUTH_TOKEN'),
        'TWILIO_PHONE_NUMBER': os.getenv('TWILIO_PHONE_NUMBER'),
    }

    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value and var_value not in ['your_account_sid_here', 'your_auth_token_here']:
            print(f"✓ {var_name}: {var_value[:8]}..." if 'TOKEN' in var_name else f"✓ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: Not configured")
            all_set = False

    return all_set


def check_twilio_credentials():
    """Verify Twilio credentials are valid"""
    print("\n" + "="*60)
    print("2. Verifying Twilio credentials...")
    print("="*60)

    try:
        from twilio.rest import Client
        from dotenv import load_dotenv

        load_dotenv()
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')

        if not account_sid or not auth_token:
            print("❌ Twilio credentials not configured in .env")
            return False

        client = Client(account_sid, auth_token)

        # Try to fetch account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✓ Twilio account validated: {account.friendly_name}")
        print(f"  Status: {account.status}")

        # Check phone number
        phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        if phone_number:
            try:
                incoming_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
                if incoming_numbers:
                    print(f"✓ Phone number configured: {phone_number}")
                    number = incoming_numbers[0]
                    print(f"  Friendly name: {number.friendly_name}")

                    # Check webhook configuration
                    if number.sms_url:
                        print(f"✓ SMS webhook configured: {number.sms_url}")
                    else:
                        print(f"⚠️  SMS webhook not configured yet")
                        print(f"   You'll need to set this in Twilio Console")
                else:
                    print(f"⚠️  Phone number {phone_number} not found in your account")
            except Exception as e:
                print(f"⚠️  Could not verify phone number: {e}")

        return True

    except Exception as e:
        print(f"❌ Twilio credentials invalid: {e}")
        print("\nPlease check your credentials at: https://console.twilio.com")
        return False


def check_server_running():
    """Check if the server is running"""
    print("\n" + "="*60)
    print("3. Checking if server is running...")
    print("="*60)

    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is running")
            print(f"  Version: {data.get('version')}")
            print(f"  Environment: {data.get('environment')}")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not running on port 8000")
        print(f"   Start it with: cd python_ai && python main.py")
        return False


def check_ngrok():
    """Check if ngrok is running (optional for local testing)"""
    print("\n" + "="*60)
    print("4. Checking ngrok (optional for webhooks)...")
    print("="*60)

    try:
        import requests
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        public_url = tunnel.get('public_url')
                        print(f"✓ ngrok is running: {public_url}")
                        print(f"\n  Configure Twilio webhook:")
                        print(f"  {public_url}/sms/webhook")
                        return True
        print("⚠️  ngrok not detected")
        print("   Start it with: ngrok http 8000")
        return False
    except:
        print("⚠️  ngrok not running")
        print("   For local testing, run: ngrok http 8000")
        print("   Not required if deploying to production server")
        return False


def test_sms_endpoint():
    """Test the SMS webhook endpoint"""
    print("\n" + "="*60)
    print("5. Testing SMS webhook endpoint...")
    print("="*60)

    try:
        import requests

        # Simulate Twilio webhook request
        test_data = {
            'From': '+15551234567',
            'Body': 'Test message',
            'MessageSid': 'TEST123'
        }

        response = requests.post(
            'http://localhost:8000/sms/webhook',
            data=test_data,
            timeout=5
        )

        if response.status_code == 200:
            print("✓ SMS webhook endpoint is working")
            print(f"  Response: {response.text[:100]}...")
            return True
        else:
            print(f"⚠️  Webhook returned status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Could not test webhook: {e}")
        return False


def main():
    """Run all checks"""
    print("\n" + "🤖 " + "="*58)
    print("   TBB Therapy Bot - Twilio Setup Verification")
    print("   " + "="*58)

    results = {
        'env': check_env_file(),
        'twilio': check_twilio_credentials(),
        'server': check_server_running(),
        'ngrok': check_ngrok(),
        'webhook': test_sms_endpoint()
    }

    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    required_checks = ['env', 'twilio', 'server']
    optional_checks = ['ngrok', 'webhook']

    required_passed = all(results[k] for k in required_checks)

    if required_passed:
        print("\n✅ All required checks passed!")
        print("\nYour bot is ready to receive SMS messages.")

        if not results['ngrok']:
            print("\n⚠️  For local testing, you need to:")
            print("   1. Run: ngrok http 8000")
            print("   2. Configure webhook in Twilio Console")

        print("\n📱 To test, send an SMS to your Twilio number!")

    else:
        print("\n❌ Some required checks failed.")
        print("\nPlease fix the issues above before testing.")

        if not results['env']:
            print("\n→ Configure your .env file with Twilio credentials")
        if not results['twilio']:
            print("\n→ Verify Twilio credentials at https://console.twilio.com")
        if not results['server']:
            print("\n→ Start the server: cd python_ai && python main.py")

    print("\n" + "="*60 + "\n")

    return 0 if required_passed else 1


if __name__ == "__main__":
    sys.exit(main())
