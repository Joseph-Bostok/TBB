#!/usr/bin/env python3
"""
Simple test script to see the bot working locally (no SMS needed)
"""

import asyncio
import sys
sys.path.insert(0, 'python_ai')

from database import init_db, AsyncSessionLocal
from memory.conversation import get_or_create_user, save_message
from routers import get_router
from experts.cbt_expert import get_cbt_expert
from experts.mindfulness_expert import get_mindfulness_expert
from experts.motivation_expert import get_motivation_expert
from event_extraction import get_event_extractor
from personalization import get_personalization_engine

async def test_bot():
    """Test the bot locally"""

    print("=" * 60)
    print("THERAPY BOT LOCAL TEST")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    await init_db()
    print("✓ Database ready")

    # Test message
    test_user = "test_user_local"
    test_message = "I have a test on Friday and I'm really stressed about it"

    print(f"\n2. Test Message: '{test_message}'")

    # Create session
    async with AsyncSessionLocal() as db:
        # Get/create user
        user, is_new = await get_or_create_user(db, test_user)
        print(f"✓ User: {test_user} ({'new' if is_new else 'existing'})")

        # Extract events
        print("\n3. Extracting events...")
        event_extractor = get_event_extractor()
        events = event_extractor.extract_events(test_message)

        if events:
            print(f"✓ Found {len(events)} event(s):")
            for event in events:
                print(f"  - Type: {event['type']}")
                print(f"  - Date: {event['date'].strftime('%A, %B %d')}")
                print(f"  - Importance: {event['importance']}")
                await event_extractor.save_event(db, user.id, event)
                print(f"  ✓ Saved to database")
        else:
            print("No events detected")

        # Route to expert
        print("\n4. Routing to expert...")
        router = get_router()
        expert_name, confidence, metadata = router.route(test_message)
        print(f"✓ Routed to: {expert_name}")
        print(f"  Confidence: {confidence:.2f}")

        # Get expert
        experts = {
            "cbt": get_cbt_expert(),
            "mindfulness": get_mindfulness_expert(),
            "motivation": get_motivation_expert()
        }
        expert = experts[expert_name]

        # Generate response
        print("\n5. Generating response...")
        response = expert.generate_response(test_message, [], metadata)
        print(f"✓ Response generated ({len(response)} chars)")

        # Apply personalization
        print("\n6. Applying personalization...")
        personalizer = get_personalization_engine()
        user_style = await personalizer.get_user_style(db, user.id)
        adapted_response = personalizer.adapt_response(response, user_style)
        print(f"✓ Response adapted to user style")

        # Save messages
        await save_message(db, user.id, "user", test_message)
        await save_message(db, user.id, "assistant", adapted_response, expert_used=expert_name)
        await db.commit()
        print("✓ Messages saved to database")

        # Show final response
        print("\n" + "=" * 60)
        print("BOT RESPONSE:")
        print("=" * 60)
        print(adapted_response)
        if events:
            print(f"\n[Event tracked: {events[0]['type']} on {events[0]['date'].strftime('%A, %B %d')}]")
        print("=" * 60)

        print("\n✓ Test completed successfully!")
        print("\nNext steps:")
        print("1. Check database: sqlite3 data/users.db")
        print("2. Start server: python python_ai/main.py")
        print("3. Set up SMS with Twilio (see QUICK_START.md)")

if __name__ == "__main__":
    asyncio.run(test_bot())
