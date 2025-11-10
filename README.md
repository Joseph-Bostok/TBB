# Therapy Bot (TTB)

AI therapy chatbot using Mixture of Experts (MoE) routing to direct conversations to specialized therapeutic approaches (CBT, Mindfulness, Motivation). Includes crisis detection and safety guardrails.

## What It Does

- **SMS Integration**: Text a real phone number (via Twilio) to chat with your therapy bot
- **Crisis Detection**: Pattern-based detection of suicidal ideation, self-harm, abuse (44 patterns)
- **MoE Routing**: Semantic embeddings route messages to appropriate expert
- **Three Experts**: CBT (anxiety/depression), Mindfulness (stress/sleep), Motivation (procrastination/goals)
- **Conversation Memory**: Context-aware responses using chat history
- **Event Tracking**: Mentions "test on Friday"? Bot remembers and follows up proactively
- **Personalization**: Learns your communication style (formality, length, emoji usage)
- **Proactive Outreach**: Scheduled check-ins before/after important events
- **Safety Features**: Incident logging, rate limiting, audit trails

## Tech Stack

- **Backend**: FastAPI (Python)
- **ML**: sentence-transformers for semantic routing
- **Database**: SQLite (async via SQLAlchemy)
- **Deployment**: Virtual environment

## Quick Start

### Option 1: Demo Mode (No SMS)
```bash
# Install
python3 -m venv venv
source venv/bin/activate
pip install -r python_ai/requirements.txt

# Run server
./venv/bin/python python_ai/main.py
# Server runs on http://localhost:8000

# Test (in new terminal)
source venv/bin/activate
python3 demo.py
```

### Option 2: SMS Mode (Text Your Bot!)
See **[SMS_SETUP_GUIDE.md](SMS_SETUP_GUIDE.md)** for complete setup instructions.

Quick version:
1. Create a Twilio account
2. Get a phone number
3. Configure `.env` with credentials
4. Expose server with ngrok
5. Set webhook URL in Twilio
6. Text your bot! 📱

## API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Send message
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "test", "message": "I feel anxious"}'

# Test routing
curl -X POST "http://localhost:8000/test-routing?message=I%20feel%20stressed"

# SMS webhook (configured in Twilio, receives incoming texts)
# POST /sms/webhook

# API docs
open http://localhost:8000/docs
```

## Architecture

```
SMS Message (Twilio) → Webhook → Rate Limit → Crisis Check → Event Extraction
                                                  ↓                 ↓
                                           Crisis Response    Save Events
                                                  ↓                 ↓
                                            MoE Router ← Conversation History
                                                  ↓
                                            Expert (CBT/Mindfulness/Motivation)
                                                  ↓
                                            Personalization (adapt to user style)
                                                  ↓
                                            Response → SMS (Twilio)
                                                  ↓
                                            Save to Database

Background Scheduler (runs every minute):
  - Check for scheduled messages
  - Send proactive follow-ups
  - Create reminders for events
```

**SMS Integration** → Twilio receives texts, forwards to webhook, bot replies via Twilio API
**Crisis Detection** → Provides immediate resources (988 Suicide Lifeline, etc.)
**Event Extraction** → Detects mentions of tests, appointments, deadlines → creates follow-ups
**MoE Router** → Encodes message, compares to expert embeddings, selects best match
**Experts** → Generate therapeutic responses using rule-based logic
**Personalization** → Adapts responses to user's style (formality, length, tone)
**Scheduler** → Proactively sends check-ins before/after important events
**Database** → Stores messages, events, scheduled messages, user profiles, safety incidents

## Project Structure

```
python_ai/
├── main.py                  # FastAPI app with SMS webhook
├── safety.py                # Crisis detection (44 patterns)
├── routers.py               # MoE semantic router
├── database.py              # SQLAlchemy models (users, messages, events, scheduled messages)
├── sms_handler.py           # Twilio SMS integration
├── personalization.py       # Communication style learning
├── event_extraction.py      # Extract events from messages
├── scheduler.py             # Proactive outreach scheduler
├── experts/                 # CBT, Mindfulness, Motivation
└── memory/                  # Embeddings & conversation history
```

## Configuration

Copy and edit `.env`:

```bash
# Copy example config
cp .env.example .env

# Key settings:
CRISIS_DETECTION_ENABLED=true
CRISIS_HOTLINE=988
MAX_MESSAGES_PER_HOUR=30
EMBEDDING_MODEL=all-MiniLM-L6-v2

# For SMS (optional):
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15551234567

# Personalization:
ENABLE_PERSONALIZATION=true
STYLE_LEARNING_WINDOW=50
```

See [SMS_SETUP_GUIDE.md](SMS_SETUP_GUIDE.md) for detailed SMS setup.

## Safety

**IMPORTANT**: This is a demo, not medical software.

- Crisis patterns detect concerning language and provide resources
- All incidents logged to database for review
- Users directed to 988 Suicide & Crisis Lifeline when needed
- Rate limiting prevents abuse

**NOT suitable for production without**:
- Licensed clinician oversight
- HIPAA compliance
- Human crisis counselor integration
- More sophisticated ML-based crisis detection

## Development

```bash
# View logs
tail -f logs/therapy_bot.log

# Check database
sqlite3 data/users.db "SELECT * FROM messages;"

# Run tests (if added)
pytest
```

## How MoE Routing Works

1. **Expert Descriptions**: Each expert has a semantic description of what it handles
2. **User Message**: Encoded into 384-dimensional vector
3. **Similarity**: Cosine similarity calculated against all expert embeddings
4. **Routing**: Highest similarity (>0.3 threshold) gets the message
5. **Response**: Selected expert generates therapeutic response

## New Features for ADHD & Mental Health Support

### 1. **Event Tracking & Proactive Follow-ups**
The bot automatically detects when you mention important events:

**Example:**
```
You: "I have a test on Friday and need to study"
Bot: "Let's work on managing that test anxiety...
      I've made a note about your test on Friday. I'll check in with you about it!"

[Thursday 9 AM]
Bot: "Hi! Your test is tomorrow. How's your preparation going?"

[Saturday 9 AM]
Bot: "How did your test go? I'd love to hear about it!"
```

Detected events: tests, exams, appointments, deadlines, interviews, presentations

### 2. **Communication Style Learning**
The bot learns YOUR style over time:
- Message length (short vs detailed)
- Emoji usage
- Formality (casual "hey" vs formal "hello")
- Tone preferences

After ~50 messages, responses adapt to match YOUR communication style.

### 3. **Proactive Check-ins**
Unlike traditional chatbots that wait for you to message:
- Daily check-ins when needed
- Pre-event anxiety support
- Post-event follow-ups
- Medication/habit reminders (coming soon)

Perfect for ADHD: **The bot reaches out to YOU** when you might forget!

## Files

- `demo.py` - Interactive demo with test scenarios
- `SMS_SETUP_GUIDE.md` - Complete guide to set up SMS texting
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `TROUBLESHOOTING.md` - Common issues and solutions

## Credits

Built with care for mental health awareness.

**Crisis Resources:**
- 🇺🇸 988 Suicide & Crisis Lifeline: Call/text **988**
- 🌍 International: [findahelpline.com](https://findahelpline.com/)
