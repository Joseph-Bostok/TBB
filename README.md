# Therapy Bot (TTB)

AI therapy chatbot using Mixture of Experts (MoE) routing to direct conversations to specialized therapeutic approaches (CBT, Mindfulness, Motivation). Includes crisis detection and safety guardrails.

## What It Does

- **Crisis Detection**: Pattern-based detection of suicidal ideation, self-harm, abuse (44 patterns)
- **MoE Routing**: Semantic embeddings route messages to appropriate expert
- **Three Experts**: CBT (anxiety/depression), Mindfulness (stress/sleep), Motivation (procrastination/goals)
- **Conversation Memory**: Context-aware responses using chat history
- **Safety Features**: Incident logging, rate limiting, audit trails

## Tech Stack

- **Backend**: FastAPI (Python)
- **ML**: sentence-transformers for semantic routing
- **Database**: SQLite (async via SQLAlchemy)
- **Deployment**: Virtual environment

## Quick Start

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

# API docs
open http://localhost:8000/docs
```

## Architecture

```
User Message → Rate Limit → Crisis Check → MoE Router → Expert → Response → DB
                                 ↓
                          Crisis Response (if detected)
```

**Crisis Detection** → Provides immediate resources (988 Suicide Lifeline, etc.)
**MoE Router** → Encodes message, compares to expert embeddings, selects best match
**Experts** → Generate therapeutic responses using rule-based logic
**Database** → Stores messages, conversation history, safety incidents

## Project Structure

```
python_ai/
├── main.py              # FastAPI app
├── safety.py            # Crisis detection (44 patterns)
├── routers.py           # MoE semantic router
├── database.py          # SQLAlchemy models
├── experts/             # CBT, Mindfulness, Motivation
└── memory/              # Embeddings & conversation history
```

## Configuration

Edit `.env`:

```bash
CRISIS_DETECTION_ENABLED=true
CRISIS_HOTLINE=988
MAX_MESSAGES_PER_HOUR=30
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

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

## Files

- `demo.py` - Interactive demo with test scenarios
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `TROUBLESHOOTING.md` - Common issues and solutions

## Credits

Built with care for mental health awareness.

**Crisis Resources:**
- 🇺🇸 988 Suicide & Crisis Lifeline: Call/text **988**
- 🌍 International: [findahelpline.com](https://findahelpline.com/)
