# 🧠 Therapy Bot (TTB) - AI-Powered Mental Health Support

An intelligent therapy chatbot that uses **Mixture of Experts (MoE)** routing with semantic embeddings to direct conversations to specialized therapeutic approaches. Built with comprehensive safety guardrails for crisis detection and intervention.

## 🎯 Project Overview

This is a **production-ready MVP** demonstrating:

- ✅ **Crisis Detection**: Real-time detection of suicidal ideation, self-harm, abuse, and other emergencies
- ✅ **Mixture of Experts (MoE)**: Semantic routing to specialized experts:
  - **CBT Expert**: Anxiety, depression, negative thought patterns
  - **Mindfulness Expert**: Stress, overwhelm, sleep problems
  - **Motivation Expert**: Procrastination, low confidence, goal-setting
- ✅ **Conversation Memory**: Contextual responses based on chat history
- ✅ **Safety First**: Audit trails, incident logging, rate limiting
- ✅ **Python-Only MVP**: Simplified from original C++/Python split for faster development

## 🏗️ Architecture

### System Flow

```
┌──────────────┐
│  SMS/User    │
│   Message    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│  FastAPI Backend (Python)                        │
│                                                   │
│  1. Rate Limiting Check                          │
│  2. Crisis Detection (Pattern Matching)          │
│     └─→ If crisis → Crisis Response + Log        │
│  3. Semantic Router (Embedding-based MoE)        │
│     ├─→ Encode message                           │
│     ├─→ Compare to expert embeddings             │
│     └─→ Select best expert                       │
│  4. Expert Response Generation                   │
│     ├─→ CBT Expert                               │
│     ├─→ Mindfulness Expert                       │
│     └─→ Motivation Expert                        │
│  5. Save to Database (SQLite)                    │
│     ├─→ Message history                          │
│     └─→ Safety incidents (if applicable)         │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Response   │
│   to User    │
└──────────────┘
```

### Directory Structure

```
TTB/
├── python_ai/                 # Main application
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration management
│   ├── database.py           # SQLAlchemy models & session
│   ├── safety.py             # Crisis detection system
│   ├── routers.py            # MoE semantic router
│   ├── logging_config.py     # Structured logging setup
│   │
│   ├── experts/              # Therapy expert modules
│   │   ├── cbt_expert.py     # CBT therapist
│   │   ├── mindfulness_expert.py  # Mindfulness coach
│   │   └── motivation_expert.py   # Motivation coach
│   │
│   ├── memory/               # Conversation context
│   │   ├── embeddings.py     # Sentence embeddings
│   │   └── conversation.py   # Message history management
│   │
│   └── requirements.txt      # Python dependencies
│
├── data/                     # Database (created on startup)
│   └── users.db             # SQLite database
│
├── logs/                    # Application logs (created on startup)
│   └── therapy_bot.log      # JSON-formatted logs
│
├── demo.py                  # Interactive demo script
├── .env.example             # Example environment configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Navigate to the project directory
cd /home/jbostok/TTB

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r python_ai/requirements.txt

# 4. Create configuration file
cp .env.example .env
# Edit .env if needed (defaults work for demo)

# 5. Create necessary directories
mkdir -p data logs
```

### Running the Server

```bash
# Start the therapy bot server
python python_ai/main.py
```

The server will start on `http://localhost:8000`

You should see output like:

```
============================================================
THERAPY BOT STARTUP
============================================================
Initializing database...
Database tables created successfully

=== Safety System Configuration ===
Crisis Detection: ENABLED
Crisis Hotline: 988
Crisis Alerts: Disabled
Detection Patterns: 47 across 6 crisis types
===================================

Therapy Bot ready on http://0.0.0.0:8000
============================================================
```

### Running the Demo

In a **new terminal** (keep the server running):

```bash
# Run the interactive demo
python demo.py
```

The demo will:
1. Test server health
2. Demonstrate semantic routing
3. Show crisis detection in action
4. Display conversation with each expert
5. Show user statistics

## 📡 API Endpoints

### POST /message

Main endpoint for user messages.

**Request:**
```json
{
  "user": "+15551234567",
  "message": "I've been feeling really anxious"
}
```

**Response:**
```json
{
  "reply": "I hear that you're going through a difficult time...",
  "expert_used": "cbt",
  "routing_confidence": 0.823,
  "crisis_detected": false,
  "crisis_type": null
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "crisis_detection": true
}
```

### GET /stats/{user_id}

Get user statistics and conversation history.

**Response:**
```json
{
  "user_id": "+15551234567",
  "total_messages": 15,
  "is_flagged": false,
  "recent_activity": {
    "message_count": 5,
    "duration_minutes": 12.3,
    "experts_used": ["cbt", "mindfulness"],
    "session_active": true
  },
  "conversation_preview": [...]
}
```

### POST /test-routing

Test semantic routing without saving messages.

**Request:**
```
POST /test-routing?message=I'm feeling anxious
```

**Response:**
```json
{
  "message": "I'm feeling anxious",
  "routed_to": "cbt",
  "confidence": 0.782,
  "all_scores": {
    "cbt": 0.782,
    "mindfulness": 0.421,
    "motivation": 0.156
  },
  "routing_reason": "Best semantic match (0.782)"
}
```

### API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛡️ Safety Features

### Crisis Detection

The bot uses pattern matching to detect crisis situations:

| Crisis Type | Examples | Response |
|------------|----------|----------|
| **Suicide** | "I want to kill myself", "I'm going to end it" | 988 Suicide & Crisis Lifeline, emergency resources |
| **Self-Harm** | "I've been cutting myself" | Crisis support, coping alternatives |
| **Harm to Others** | "I want to hurt someone" | Immediate professional help direction |
| **Abuse** | "He hits me" | Domestic violence hotline, safety resources |
| **Substance** | "I overdosed" | 911 / emergency services |

**Severity Levels:**
- 🔴 **Critical**: Immediate danger (e.g., "I'm going to kill myself tonight")
- 🟠 **High**: Clear intent or planning
- 🟡 **Medium**: Concerning ideation, no immediate plan

### Safety Incident Logging

All detected crises are logged to the database:

```python
SafetyIncident(
    user_id=123,
    message_id=456,
    incident_type="suicide",
    severity="high",
    detected_keywords=["kill myself"],
    action_taken="Provided 988 crisis resources",
    resolved=False
)
```

### Rate Limiting

Default: **30 messages per hour** per user to prevent abuse.

Configurable in `.env`:
```bash
MAX_MESSAGES_PER_HOUR=30
```

## 🤖 Mixture of Experts (MoE)

### How Routing Works

1. **Encode Message**: User message → embedding vector (384 dimensions)
2. **Compare to Experts**: Calculate cosine similarity to each expert's description
3. **Select Expert**: Choose highest similarity above confidence threshold (0.3)
4. **Generate Response**: Selected expert creates therapeutic response

### Expert Specializations

#### 🧠 CBT Expert
- **Handles**: Anxiety, depression, negative thoughts, rumination
- **Techniques**: Socratic questioning, cognitive restructuring, thought challenging
- **Example**: "I can't stop worrying" → CBT techniques for examining worried thoughts

#### 🧘 Mindfulness Expert
- **Handles**: Stress, overwhelm, sleep, difficulty focusing
- **Techniques**: Breathing exercises, body scan, grounding, meditation
- **Example**: "I'm so stressed" → Guided breathing exercise (4-7-8 technique)

#### 💪 Motivation Expert
- **Handles**: Procrastination, low confidence, goal-setting, feeling stuck
- **Techniques**: SMART goals, self-compassion, values clarification, reframing failure
- **Example**: "I have no motivation" → Action > Motivation principle, tiny steps

### Routing Example

```
Message: "I can't stop worrying about everything"

Similarity Scores:
  CBT:        0.85  ← Selected (highest)
  Mindfulness: 0.42
  Motivation: 0.18

Routed to: CBT Expert
Confidence: 0.85
```

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,  -- Phone number or identifier
    created_at DATETIME,
    last_active DATETIME,
    message_count INTEGER,
    is_flagged BOOLEAN,            -- Has triggered crisis detection
    preferred_expert TEXT
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,               -- Foreign key to users
    role TEXT,                     -- 'user' or 'assistant'
    content TEXT,
    expert_used TEXT,              -- 'cbt', 'mindfulness', 'motivation', 'crisis'
    timestamp DATETIME
);
```

### Safety Incidents Table
```sql
CREATE TABLE safety_incidents (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,               -- Foreign key to users
    message_id INTEGER,            -- Foreign key to messages
    incident_type TEXT,            -- 'suicide', 'self_harm', etc.
    severity TEXT,                 -- 'critical', 'high', 'medium', 'low'
    detected_keywords TEXT,        -- JSON array of matched patterns
    action_taken TEXT,
    resolved BOOLEAN,
    timestamp DATETIME
);
```

### Inspecting the Database

```bash
# View all tables
sqlite3 data/users.db ".tables"

# View users
sqlite3 data/users.db "SELECT * FROM users;"

# View safety incidents
sqlite3 data/users.db "SELECT * FROM safety_incidents;"

# View conversation for a user
sqlite3 data/users.db "SELECT role, content FROM messages WHERE user_id=1 ORDER BY timestamp;"
```

## 📊 Logging

Logs are written to `logs/therapy_bot.log` in JSON format for easy parsing.

**View logs:**
```bash
# Tail logs in real-time
tail -f logs/therapy_bot.log

# View last 50 lines
tail -n 50 logs/therapy_bot.log

# Pretty-print JSON logs
cat logs/therapy_bot.log | jq '.'
```

**Log Levels:**
- `INFO`: Normal operations (requests, routing decisions)
- `WARNING`: Concerns (crisis detected, rate limits)
- `ERROR`: Failures (database errors, exceptions)

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Application
APP_NAME=TherapyBot
ENVIRONMENT=development           # development | production

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/users.db

# Safety
CRISIS_DETECTION_ENABLED=true
CRISIS_HOTLINE=988
CRISIS_ALERT_EMAIL=               # Optional: admin@example.com

# Models
USE_MOCK_MODELS=true              # Use rule-based experts (no API keys needed)
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Sentence transformer model

# Rate Limiting
MAX_MESSAGES_PER_HOUR=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/therapy_bot.log
```

## 🔬 Testing

### Manual Testing

Use `curl` or the demo script:

```bash
# Send a message
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "test_user", "message": "I feel anxious"}'

# Test routing
curl -X POST "http://localhost:8000/test-routing?message=I%20need%20to%20relax"

# Check health
curl http://localhost:8000/health
```

### Automated Demo

```bash
python demo.py
```

This runs through all test scenarios including crisis detection.

## 📈 Production Considerations

### What's Production-Ready

✅ **Safety System**: Crisis detection with pattern matching
✅ **Database**: SQLAlchemy with async support
✅ **Logging**: Structured JSON logs
✅ **Rate Limiting**: Configurable per-user limits
✅ **API**: FastAPI with validation and documentation
✅ **Error Handling**: Graceful failures with proper HTTP codes

### What Needs Enhancement for Production

⚠️ **Replace Mock Experts**: Integrate real LLMs (OpenAI, Anthropic)
⚠️ **Enhance Crisis Detection**: Add ML-based detection (not just patterns)
⚠️ **Human Oversight**: Route critical incidents to human counselors
⚠️ **SMS Integration**: Connect to Twilio or similar service
⚠️ **Authentication**: Add API keys or OAuth
⚠️ **Scalability**: Use PostgreSQL instead of SQLite
⚠️ **Monitoring**: Add Sentry, DataDog, or similar
⚠️ **HIPAA Compliance**: Encrypt data, audit trails, business associate agreements
⚠️ **Job Queue**: Add Celery/Redis for async processing (if needed)

### Integrating Real LLMs

Replace the expert implementations with LLM calls:

```python
# Example: Using OpenAI in cbt_expert.py
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def generate_response(self, user_message, history, context):
    # Build context from conversation history
    messages = [
        {"role": "system", "content": "You are a CBT therapist..."},
        *history,
        {"role": "user", "content": user_message}
    ]

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content
```

## 🤔 Design Decisions Explained

### Why Python-Only (Not C++)?

**Original plan**: C++ backend for performance, Python for AI.

**MVP decision**: Python-only for faster iteration.

**Reasoning**:
- SMS has inherent latency (seconds), so microsecond optimizations don't matter
- Python has rich AI/ML ecosystem
- Easier to deploy and maintain
- Can optimize later if needed

**When to add C++ layer**:
- High message volume (>1000 req/sec)
- Complex message routing logic
- Real-time performance requirements

### Why Semantic Routing Instead of Classification?

**Alternative**: Train a classifier to categorize messages.

**Our approach**: Embedding similarity.

**Why**:
- ✅ No labeled training data needed
- ✅ Easy to add new experts (just add description)
- ✅ Works out-of-box with pretrained models
- ✅ Transparent (can inspect similarity scores)

**Trade-off**: Slightly lower accuracy than a fine-tuned classifier, but much easier to build and maintain.

### Why Pattern Matching for Crisis Detection?

**Alternative**: ML-based crisis detection model.

**Our approach**: Regex pattern matching.

**Why**:
- ✅ Transparent and auditable (can see what triggered)
- ✅ Zero false negatives for common phrases
- ✅ No model training required
- ✅ Instant response (no inference latency)

**For production**: Combine both (patterns for high-confidence, ML for nuanced cases).

## 📚 Further Reading

### Mental Health Chatbots
- [Crisis Text Line](https://www.crisistextline.org/) - Real-world crisis intervention via text
- [Woebot](https://woebothealth.com/) - CBT-based mental health chatbot
- [Ethics of Mental Health Chatbots](https://arxiv.org/abs/2011.13740)

### Mixture of Experts
- [Switch Transformers](https://arxiv.org/abs/2101.03961) - Google's MoE architecture
- [Semantic Router](https://github.com/aurelio-labs/semantic-router) - Library for semantic routing

### Crisis Detection
- [Suicide Risk Assessment via Text](https://aclanthology.org/2020.clpsych-1.16/)
- [CLPsych Shared Tasks](https://clpsych.org/) - NLP for mental health

## 🙏 Ethical Considerations

**This is a DEMONSTRATION project, not medical software.**

### Critical Warnings

⚠️ **NOT A REPLACEMENT FOR THERAPY**: This bot cannot replace professional mental health care.

⚠️ **CRISIS LIMITATIONS**: Pattern matching cannot catch all crises. Some users in danger may not use detectable language.

⚠️ **FALSE SENSE OF SECURITY**: Users may over-rely on the bot instead of seeking real help.

⚠️ **PRIVACY**: Conversations contain sensitive health information requiring strict protection.

⚠️ **MANDATORY REPORTING**: Some jurisdictions require reporting of child abuse, imminent harm, etc.

### Recommendations for Real Deployment

1. **Clear Disclaimers**: Every interaction should clarify this is AI, not a therapist
2. **Crisis Escalation**: Route emergencies to human counselors
3. **Informed Consent**: Users must understand data collection and limitations
4. **Professional Oversight**: Licensed clinicians should oversee the system
5. **Regular Audits**: Review safety incidents and false negatives
6. **User Safety**: Provide resources (hotlines, local services) prominently

## 📝 License

This is a demonstration project. Use at your own risk.

For production deployment of mental health software, consult:
- Healthcare attorneys (HIPAA, liability)
- Licensed mental health professionals
- Ethics review boards

## 🐛 Issues & Feedback

This is a demo project. For a real therapy bot:
- Hire licensed mental health professionals
- Conduct rigorous safety testing
- Implement clinical oversight
- Consider regulatory requirements (FDA, HIPAA, etc.)

---

**Built with care for mental health awareness. If you or someone you know is in crisis, please contact:**
- 🇺🇸 988 Suicide & Crisis Lifeline: Call or text **988**
- 🌍 International: [Find local crisis resources](https://findahelpline.com/)
# TBB
