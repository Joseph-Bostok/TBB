#!/usr/bin/env python3
"""
Quick test to verify Claude API key is working
"""
from anthropic import Anthropic

# Read API key directly from .env file
def get_api_key():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading .env: {e}")
    return None

def test_claude():
    """Test Claude API connection"""

    print("=" * 60)
    print("CLAUDE API TEST")
    print("=" * 60)

    api_key = get_api_key()

    if not api_key:
        print("\n❌ ANTHROPIC_API_KEY not found in .env file")
        return

    if api_key.startswith('sk-ant-'):
        print(f"\n✓ API Key found: {api_key[:20]}...")
    else:
        print(f"\n⚠️  API Key format unexpected: {api_key[:20]}...")

    print("\nTesting Claude API connection...")

    try:
        client = Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": "Say hello and confirm you're working! Keep it very brief."
            }]
        )

        response_text = message.content[0].text

        print("\n" + "=" * 60)
        print("✅ SUCCESS! Claude responded:")
        print("=" * 60)
        print(response_text)
        print("=" * 60)
        print("\n✓ Your Claude API key is working correctly!")
        print("✓ Cost for this test: ~$0.001 (tenth of a penny)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("1. API key is invalid")
        print("2. No credits in your Anthropic account")
        print("3. Network connection issue")

if __name__ == "__main__":
    test_claude()
