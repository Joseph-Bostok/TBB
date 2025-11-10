#!/usr/bin/env python3
"""
Therapy Bot Demo Script

This script demonstrates all the key features of the therapy bot:
1. Crisis detection and intervention
2. Semantic routing to different experts
3. Conversation memory
4. Rate limiting
5. Safety incident tracking

Run this after starting the server with:
    python python_ai/main.py

The demo sends test messages and shows the bot's responses.
"""

import asyncio
import httpx
import json
from typing import Dict, List
import sys


# ==================== Configuration ====================

BASE_URL = "http://localhost:8000"
DEMO_USER = "demo_user_123"


# ==================== Test Scenarios ====================

TEST_SCENARIOS = [
    {
        "category": "🧠 CBT Expert - Anxiety",
        "messages": [
            "I've been feeling really anxious lately",
            "I can't stop worrying about everything",
            "My mind keeps racing with negative thoughts",
        ]
    },
    {
        "category": "🧘 Mindfulness Expert - Stress",
        "messages": [
            "I'm so stressed out, I can't relax",
            "I can't sleep at night, my mind won't shut off",
            "I feel overwhelmed with everything going on",
        ]
    },
    {
        "category": "💪 Motivation Expert - Procrastination",
        "messages": [
            "I have no motivation to do anything",
            "I keep procrastinating on my work",
            "I feel like I'm not good enough and keep giving up",
        ]
    },
    {
        "category": "🚨 CRISIS DETECTION - Suicide",
        "messages": [
            "I want to kill myself",  # Will trigger crisis response
        ]
    },
    {
        "category": "🚨 CRISIS DETECTION - Self-Harm",
        "messages": [
            "I've been cutting myself again",  # Will trigger crisis response
        ]
    },
]


# ==================== Helper Functions ====================

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_message(role: str, content: str, metadata: Dict = None):
    """Print a formatted message"""
    if role == "USER":
        print(f"👤 USER:")
        print(f"   {content}")
    else:
        print(f"🤖 BOT:")
        # Indent bot response for readability
        for line in content.split('\n'):
            print(f"   {line}")

        # Show metadata
        if metadata:
            print(f"\n   📊 Metadata:")
            if metadata.get('expert_used'):
                print(f"      Expert: {metadata['expert_used']}")
            if metadata.get('routing_confidence') is not None:
                print(f"      Confidence: {metadata['routing_confidence']:.3f}")
            if metadata.get('crisis_detected'):
                print(f"      ⚠️  CRISIS DETECTED: {metadata.get('crisis_type', 'unknown')}")
    print()


async def send_message(client: httpx.AsyncClient, user: str, message: str) -> Dict:
    """
    Send a message to the bot

    Args:
        client: HTTP client
        user: User identifier
        message: Message text

    Returns:
        Dict: Response from the bot
    """
    try:
        response = await client.post(
            f"{BASE_URL}/message",
            json={"user": user, "message": message},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def test_health_check(client: httpx.AsyncClient):
    """Test the health check endpoint"""
    print_section("🏥 HEALTH CHECK")

    try:
        response = await client.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()

        print(f"✅ Server Status: {data['status']}")
        print(f"   Version: {data['version']}")
        print(f"   Environment: {data['environment']}")
        print(f"   Crisis Detection: {'Enabled ✅' if data['crisis_detection'] else 'Disabled ⚠️'}")

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure the server is running:")
        print("   python python_ai/main.py")
        sys.exit(1)


async def test_routing(client: httpx.AsyncClient):
    """Test the routing endpoint"""
    print_section("🔀 TESTING SEMANTIC ROUTER")

    test_messages = [
        "I'm feeling anxious and worried",
        "I need to calm down and relax",
        "I have no motivation to work",
    ]

    for msg in test_messages:
        try:
            response = await client.post(
                f"{BASE_URL}/test-routing",
                params={"message": msg}
            )
            response.raise_for_status()
            data = response.json()

            print(f"Message: '{msg}'")
            print(f"Routed to: {data['routed_to']} (confidence: {data['confidence']})")
            print(f"All scores: {data['all_scores']}")
            print()

        except Exception as e:
            print(f"❌ Routing test failed: {e}")


async def run_scenario(client: httpx.AsyncClient, scenario: Dict):
    """
    Run a test scenario

    Args:
        client: HTTP client
        scenario: Scenario dict with category and messages
    """
    print_section(scenario['category'])

    for message in scenario['messages']:
        print_message("USER", message)

        response = await send_message(client, DEMO_USER, message)

        if response:
            print_message(
                "BOT",
                response['reply'],
                metadata={
                    'expert_used': response.get('expert_used'),
                    'routing_confidence': response.get('routing_confidence'),
                    'crisis_detected': response.get('crisis_detected'),
                    'crisis_type': response.get('crisis_type'),
                }
            )

        # Small delay between messages for readability
        await asyncio.sleep(0.5)


async def show_user_stats(client: httpx.AsyncClient):
    """Show statistics for the demo user"""
    print_section("📊 USER STATISTICS")

    try:
        response = await client.get(f"{BASE_URL}/stats/{DEMO_USER}")
        response.raise_for_status()
        data = response.json()

        print(f"User ID: {data['user_id']}")
        print(f"Total Messages: {data['total_messages']}")
        print(f"Flagged for Safety: {'Yes ⚠️' if data['is_flagged'] else 'No'}")
        print(f"\nRecent Activity (last hour):")
        print(f"  Messages: {data['recent_activity']['message_count']}")
        print(f"  Duration: {data['recent_activity']['duration_minutes']:.1f} minutes")
        print(f"  Experts Used: {', '.join(data['recent_activity']['experts_used']) if data['recent_activity']['experts_used'] else 'None'}")
        print(f"  Session Active: {'Yes' if data['recent_activity']['session_active'] else 'No'}")

        print(f"\nConversation Preview (last 5 messages):")
        for msg in data['conversation_preview']:
            role = msg['role'].upper()
            content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
            print(f"  [{role}] {content}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"No statistics available yet for user: {DEMO_USER}")
        else:
            print(f"❌ Error fetching stats: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_rate_limiting(client: httpx.AsyncClient):
    """Test rate limiting by sending many messages"""
    print_section("⏱️  TESTING RATE LIMITING")

    print("Sending 35 messages to test rate limit (max: 30/hour)...\n")

    test_user = "rate_limit_test_user"

    for i in range(35):
        response = await send_message(client, test_user, f"Test message {i+1}")

        if response:
            print(f"✅ Message {i+1}: Accepted")
        else:
            print(f"⛔ Message {i+1}: Rate limit reached!")
            print(f"   Successfully sent {i} messages before hitting the limit.")
            break

        # Don't delay - we want to hit the limit
        if i < 34:
            await asyncio.sleep(0.1)

    print()


# ==================== Main Demo ====================

async def main():
    """
    Main demo function

    This runs through all test scenarios and demonstrates the bot's capabilities.
    """

    print("\n" + "="*70)
    print("  🧠 THERAPY BOT - INTERACTIVE DEMO")
    print("="*70)
    print("\nThis demo will showcase:")
    print("  ✅ Crisis detection and safety interventions")
    print("  ✅ Semantic routing to expert therapists (CBT, Mindfulness, Motivation)")
    print("  ✅ Conversation memory and context")
    print("  ✅ Rate limiting for abuse prevention")
    print("  ✅ User statistics and analytics")
    print()
    input("Press Enter to begin the demo...")

    async with httpx.AsyncClient() as client:

        # 1. Health check
        await test_health_check(client)
        input("\nPress Enter to continue...")

        # 2. Test routing
        await test_routing(client)
        input("\nPress Enter to continue...")

        # 3. Run conversation scenarios
        for scenario in TEST_SCENARIOS:
            await run_scenario(client, scenario)
            input("\nPress Enter to continue to next scenario...")

        # 4. Show user statistics
        await show_user_stats(client)
        input("\nPress Enter to continue...")

        # 5. Test rate limiting (optional - commented out by default as it's verbose)
        # Uncomment to test:
        # await test_rate_limiting(client)

    print_section("✅ DEMO COMPLETE")
    print("Key Takeaways:")
    print("  1. Crisis messages trigger immediate safety interventions")
    print("  2. Different concerns route to specialized experts")
    print("  3. All conversations are saved for context and continuity")
    print("  4. Rate limiting prevents abuse")
    print("  5. Safety incidents are logged for review")
    print()
    print("To explore further:")
    print("  - View logs: cat logs/therapy_bot.log")
    print("  - View database: sqlite3 data/users.db")
    print("  - API docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
