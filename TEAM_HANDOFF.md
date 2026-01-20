# TBB Therapy Bot - Team Handoff Document

## Quick Start for New Developers

Welcome to the TBB Therapy Bot project! This document will get you up to speed quickly.

---

## 🎯 What Is This Project?

An AI-powered mental health support chatbot accessible via SMS. Users text a phone number, and an AI therapist responds instantly 24/7. No app required.

**Think:** Crisis Text Line meets ChatGPT meets professional therapy.

---

## 📚 Essential Reading (in order)

1. **Start here:** `README.md` - Project overview
2. **Architecture:** `SYSTEM_DESIGN.md` - Complete technical design (60 pages)
3. **Product:** `PRODUCT_REQUIREMENTS.md` - Features, user stories, metrics
4. **Setup:** `TWILIO_SETUP_CHECKLIST.md` - How to get SMS working
5. **Alternative:** `FIREBASE_SETUP_GUIDE.md` - Phone auth (optional)

---

## 🏗 Architecture at a Glance

```
User texts phone number
        ↓
    Twilio SMS
        ↓
    FastAPI Backend
        ↓
    Crisis Detection → Route to Expert (CBT/Mindfulness/Motivation)
        ↓
    Claude AI generates response
        ↓
    Save to database
        ↓
    Send SMS back to user
```

**Key Technologies:**
- **Backend:** Python 3.10+, FastAPI
- **Database:** SQLite (dev), PostgreSQL (prod)
- **AI:** Claude API (Anthropic), Sentence Transformers
- **SMS:** Twilio
- **Deployment:** Docker, AWS/GCP

---

## 📂 Project Structure

```
TBB/
├── python_ai/                    # Main application code
│   ├── main.py                   # FastAPI app, endpoints
│   ├── config.py                 # Configuration management
│   ├── database.py               # SQLAlchemy models
│   ├── safety.py                 # Crisis detection
│   ├── routers.py                # Semantic routing (MoE)
│   ├── sms_handler.py            # Twilio SMS integration
│   ├── firebase_auth.py          # Firebase phone auth
│   ├── scheduler.py              # Proactive message scheduling
│   ├── event_extraction.py       # Extract important dates
│   ├── personalization.py        # User style adaptation
│   │
│   ├── experts/                  # Therapy expert modules
│   │   ├── cbt_expert.py         # Cognitive Behavioral Therapy
│   │   ├── mindfulness_expert.py # Mindfulness techniques
│   │   ├── motivation_expert.py  # Motivational support
│   │   └── claude_expert.py      # General LLM expert
│   │
│   ├── memory/                   # Conversation memory
│   │   └── conversation.py       # History retrieval, user management
│   │
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables (not in git)
│
├── data/                         # SQLite database (generated)
├── logs/                         # Application logs (generated)
│
├── SYSTEM_DESIGN.md              # Complete technical design doc
├── PRODUCT_REQUIREMENTS.md       # Product specs and features
├── TWILIO_SETUP_CHECKLIST.md    # SMS setup guide
├── FIREBASE_SETUP_GUIDE.md       # Phone auth guide
├── START_SMS_BOT.sh              # Quick start script
├── test_twilio_setup.py          # Setup verification script
├── test-phone-auth.html          # Firebase auth test page
│
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project README
```

---

## 🚀 Getting Started

### 1. Clone & Setup

```bash
# Clone the repo
git clone <repo-url>
cd TBB

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r python_ai/requirements.txt

# Create directories
mkdir -p python_ai/data
mkdir -p python_ai/logs

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add:

```bash
# Claude AI API Key (required)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Firebase (optional - for phone auth)
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/users.db
```

### 3. Run the Server

```bash
cd python_ai
python main.py

# Or use the quick start script:
cd ..
./START_SMS_BOT.sh
```

Server runs on: http://localhost:8000

### 4. Test It

```bash
# Health check
curl http://localhost:8000/health

# Test message endpoint
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "testuser", "message": "I feel anxious"}'

# Verify setup
python test_twilio_setup.py
```

---

## 🔑 Key Concepts

### 1. Crisis Detection
**File:** `python_ai/safety.py`

Every incoming message is scanned for crisis keywords:
- Suicide: "kill myself", "end it all", "not worth living"
- Self-harm: "cut myself", "hurt myself"
- Abuse: "hitting me", "touching me"

If detected:
1. Immediate crisis response generated
2. Safety incident logged to database
3. User flagged for follow-up
4. Optional alert to human moderator

**Key function:** `detect_crisis(message: str) -> CrisisResult`

---

### 2. Semantic Routing (Mixture of Experts)
**File:** `python_ai/routers.py`

Not all messages need the same expert. We route based on content:

- **CBT Expert:** Negative thoughts, cognitive distortions
- **Mindfulness Expert:** Anxiety, panic, overwhelm
- **Motivation Expert:** Goals, achievements, encouragement

**Algorithm:**
```python
1. Convert message to embedding (sentence-transformers)
2. Calculate cosine similarity with expert prototypes
3. Select expert with highest similarity
4. Confidence threshold: 0.6
```

**Key function:** `route_message(message: str) -> (expert, confidence)`

---

### 3. Conversation Memory
**File:** `python_ai/memory/conversation.py`

The bot remembers everything:
- Last 10 messages by default (configurable)
- Stored in `messages` table with timestamps
- Retrieved and formatted for LLM context

**Key functions:**
- `get_conversation_history(user_id, limit=10)`
- `save_message(user_id, role, content, expert_used)`
- `get_or_create_user(user_identifier) -> (User, is_new)`

---

### 4. Event Extraction & Proactive Outreach
**Files:** `event_extraction.py`, `scheduler.py`

AI extracts important dates from conversation:
- "I have an exam next Friday" → Creates ImportantEvent
- Schedules check-in message for Thursday
- Schedules follow-up message for Saturday

**Scheduler:**
- APScheduler runs every 1 minute
- Checks `scheduled_messages` table for due messages
- Sends via Twilio SMS
- Marks as sent

**Key functions:**
- `extract_important_events(conversation_text)`
- `schedule_proactive_messages(event, user_id)`

---

### 5. Personalization
**File:** `python_ai/personalization.py`

Adapts to user's style:
- Message length (short vs. verbose)
- Formality (casual vs. professional)
- Emoji usage
- Topics of interest

**Storage:** `User.communication_style` (JSON column)

**Key function:** `learn_communication_style(user_id, message_history)`

---

## 🗄 Database Schema

### Tables

**users** - User profiles
```sql
- id (PK)
- user_id (phone number, unique)
- created_at
- last_active
- message_count
- is_flagged (crisis flag)
- preferred_expert
- communication_style (JSON)
```

**messages** - Conversation history
```sql
- id (PK)
- user_id (FK)
- role (user/assistant)
- content
- expert_used
- timestamp
```

**safety_incidents** - Crisis events
```sql
- id (PK)
- user_id (FK)
- message_id (FK)
- incident_type (suicide, self_harm, etc.)
- severity (low/medium/high/critical)
- detected_keywords (JSON)
- action_taken
- resolved
- timestamp
```

**important_events** - User's important dates
```sql
- id (PK)
- user_id (FK)
- event_type (test, appointment, deadline, etc.)
- description
- event_date
- importance
- follow_up_before_days (CSV)
- follow_up_after_days (CSV)
- completed
```

**scheduled_messages** - Proactive outreach queue
```sql
- id (PK)
- user_id (FK)
- related_event_id (FK)
- message_content
- message_type
- scheduled_time
- sent (boolean)
- sent_at
```

---

## 🔌 API Endpoints

### Public Endpoints

#### POST `/sms/webhook`
Receives incoming SMS from Twilio
```bash
curl -X POST http://localhost:8000/sms/webhook \
  -d "From=+15551234567" \
  -d "Body=I feel anxious"
```

#### POST `/message`
Send message to bot (API)
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "+15551234567", "message": "I feel anxious"}'
```

#### POST `/auth/verify-phone`
Verify phone via Firebase
```bash
curl -X POST http://localhost:8000/auth/verify-phone \
  -H "Content-Type: application/json" \
  -d '{"id_token": "eyJhbGci..."}'
```

#### GET `/health`
Health check
```bash
curl http://localhost:8000/health
```

#### GET `/stats/{user_id}`
User statistics
```bash
curl http://localhost:8000/stats/+15551234567
```

**Full API docs:** http://localhost:8000/docs (Swagger UI)

---

## 🧪 Testing

### Unit Tests
```bash
pytest python_ai/tests/
```

### Manual Testing

**Test SMS flow locally:**
```bash
# 1. Start server
python main.py

# 2. Simulate Twilio webhook
curl -X POST http://localhost:8000/sms/webhook \
  -d "From=+15551234567" \
  -d "Body=I'm feeling anxious" \
  -d "MessageSid=TEST123"
```

**Test crisis detection:**
```python
from safety import detect_crisis

result = detect_crisis("I want to kill myself")
assert result.is_crisis == True
assert result.severity == "critical"
```

**Test routing:**
```python
from routers import get_router

router = get_router()
expert, confidence = router.route("I can't stop thinking negative thoughts")
assert expert == "cbt"
```

---

## 🐛 Debugging

### View Logs
```bash
# Real-time logs
tail -f python_ai/logs/therapy_bot.log

# Search for errors
grep ERROR python_ai/logs/therapy_bot.log

# View specific user
grep "+15551234567" python_ai/logs/therapy_bot.log
```

### Database Inspection
```bash
# Open database
sqlite3 python_ai/data/users.db

# View users
SELECT * FROM users;

# View recent messages
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;

# View crisis incidents
SELECT * FROM safety_incidents WHERE resolved = 0;
```

### ngrok Inspection
When using ngrok for webhooks:
- Dashboard: http://localhost:4040
- Shows all HTTP requests/responses
- Replay requests for debugging

---

## 🚨 Common Issues

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Fix:** Install dependencies
```bash
pip install -r python_ai/requirements.txt
```

### Issue: "unable to open database file"
**Fix:** Create data directory
```bash
mkdir -p python_ai/data
```

### Issue: "Firebase credentials file not found"
**Fix:** Either add the file or comment out Firebase in main.py
```bash
# Option 1: Add file
cp /path/to/firebase-creds.json firebase-credentials.json

# Option 2: Disable Firebase
# Comment out firebase import in main.py
```

### Issue: "Twilio webhook not receiving messages"
**Fix:** Check webhook URL in Twilio Console
1. Verify ngrok is running
2. Get ngrok URL: `curl http://localhost:4040/api/tunnels`
3. Update Twilio: https://console.twilio.com → Phone Numbers → Configure

### Issue: "Claude API rate limit exceeded"
**Fix:** Implement exponential backoff or upgrade plan
- Free tier: 50 requests/minute
- Paid tier: 1000 requests/minute

---

## 📊 Monitoring

### Key Metrics to Watch

**Technical:**
- Response time (target: < 2s)
- Error rate (target: < 1%)
- Uptime (target: 99.9%)

**Product:**
- Daily active users
- Messages per user
- Crisis incidents per day
- User retention (7-day, 30-day)

**Cost:**
- Twilio spend (SMS volume)
- Claude API spend (token usage)
- Infrastructure spend

### Logging Best Practices

```python
# Good logging
logger.info(f"Message received from {user_id}", extra={
    "user_id": user_id,
    "expert_used": "cbt",
    "crisis_detected": False,
    "response_time_ms": 234
})

# Bad logging
print("Got message")  # Don't use print()
logger.info("Processing...")  # Not informative
```

---

## 🔒 Security Checklist

- [ ] Environment variables in `.env`, not in code
- [ ] `.env` is in `.gitignore`
- [ ] Firebase credentials not committed
- [ ] Twilio webhook signature validation enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Database backups automated
- [ ] HTTPS in production
- [ ] Secrets rotated regularly
- [ ] Audit logs for data access

---

## 🚀 Deployment

### Development
```bash
python main.py
```

### Staging (with Docker)
```bash
docker build -t tbb-bot:staging .
docker run -p 8000:8000 --env-file .env tbb-bot:staging
```

### Production (AWS example)
```bash
# 1. Build and push image
docker build -t tbb-bot:prod .
docker tag tbb-bot:prod <aws-account>.dkr.ecr.us-east-1.amazonaws.com/tbb-bot:prod
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/tbb-bot:prod

# 2. Deploy to ECS
aws ecs update-service --cluster tbb-cluster --service tbb-service --force-new-deployment

# 3. Verify health
curl https://api.tbbtherapy.com/health
```

---

## 📞 Getting Help

### Documentation
- **System Design:** Read `SYSTEM_DESIGN.md` (comprehensive)
- **API Docs:** http://localhost:8000/docs (auto-generated)
- **Product Specs:** `PRODUCT_REQUIREMENTS.md`

### External Resources
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Twilio: https://www.twilio.com/docs
- Claude AI: https://docs.anthropic.com/
- Sentence Transformers: https://www.sbert.net/

### Team Contacts
- **Tech Lead:** [TBD]
- **Product Manager:** [TBD]
- **DevOps:** [TBD]
- **Clinical Advisor:** [TBD]

---

## 🎯 Quick Commands Reference

```bash
# Start server
python python_ai/main.py

# Or use quick start script
./START_SMS_BOT.sh

# Start ngrok (for webhooks)
ngrok http 8000

# Run tests
pytest

# Verify setup
python test_twilio_setup.py

# View logs
tail -f python_ai/logs/therapy_bot.log

# Database shell
sqlite3 python_ai/data/users.db

# Install dependencies
pip install -r python_ai/requirements.txt

# Format code
black python_ai/

# Type checking
mypy python_ai/
```

---

## ✅ Developer Onboarding Checklist

### Day 1
- [ ] Clone repository
- [ ] Read this handoff document
- [ ] Set up development environment
- [ ] Run server locally
- [ ] Test health endpoint
- [ ] Read `SYSTEM_DESIGN.md` (skim for overview)

### Week 1
- [ ] Read `PRODUCT_REQUIREMENTS.md`
- [ ] Understand crisis detection system
- [ ] Understand semantic routing
- [ ] Send test messages
- [ ] Inspect database schema
- [ ] Review key code files (main.py, safety.py, routers.py)

### Week 2
- [ ] Make first code change (small bug fix or feature)
- [ ] Write unit tests
- [ ] Deploy to staging
- [ ] Review deployment process
- [ ] Set up monitoring access

### Week 3
- [ ] Participate in on-call rotation
- [ ] Debug production issue
- [ ] Optimize a slow query
- [ ] Review architecture decisions
- [ ] Suggest improvements

---

## 🏆 Code Standards

### Python Style
- Follow PEP 8
- Use `black` for formatting
- Type hints preferred
- Docstrings for public functions

### Git Workflow
- Branch naming: `feature/description` or `bug/description`
- Commit messages: `Fix crisis detection for edge case`
- PR reviews: 2 approvals required
- Squash merge to main

### Testing
- Unit tests for business logic
- Integration tests for endpoints
- E2E tests for critical flows
- Coverage target: 80%+

---

## 🎉 You're Ready!

You now have everything you need to contribute to TBB Therapy Bot. The code is well-structured, documented, and ready for scale.

**Remember:**
- This is healthcare software - safety first
- Every line of code could help someone in crisis
- Ask questions - mental health is complex
- Test thoroughly - lives may depend on it

**Welcome to the team! Let's build something that helps people.** 💙

---

**Document Version:** 1.0
**Last Updated:** January 20, 2025
**Maintained By:** Engineering Team
