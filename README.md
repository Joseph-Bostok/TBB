# TBB Therapy Bot

**AI-powered mental health support via SMS - No app required.**

Text a phone number, get therapy from specialized AI experts 24/7. Built with crisis detection, conversation memory, and proactive outreach.

---

## 🎯 What Is This?

An SMS chatbot that provides mental health support through evidence-based therapeutic approaches. Users text a phone number and receive immediate support from specialized AI experts trained in:

- **CBT** (Cognitive Behavioral Therapy) - Anxiety, depression, negative thinking
- **Mindfulness** - Stress, panic, meditation techniques
- **Motivation** - Goals, procrastination, encouragement

**Key Features:**
- ✅ **Crisis Detection** - Identifies concerning language and provides immediate help
- ✅ **Conversation Memory** - Remembers everything you've discussed
- ✅ **Event Tracking** - "Exam next Friday" → Bot remembers and checks in
- ✅ **Proactive Outreach** - Scheduled messages before/after important events
- ✅ **Personalization** - Adapts to your communication style
- ✅ **SMS-First** - Works on any phone, no app required

---

## 📚 Documentation

### For Developers
- **[TEAM_HANDOFF.md](TEAM_HANDOFF.md)** - Start here! Quick onboarding guide
- **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)** - Complete technical architecture (60 pages)
- **[PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md)** - Features, metrics, roadmap

### For Setup
- **[TWILIO_SETUP_CHECKLIST.md](TWILIO_SETUP_CHECKLIST.md)** - SMS setup guide
- **[FIREBASE_SETUP_GUIDE.md](FIREBASE_SETUP_GUIDE.md)** - Phone authentication (optional)
- **[SMS_QUICKSTART.md](SMS_QUICKSTART.md)** - Quick start for SMS bot

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Twilio account (for SMS)
- Claude API key (for AI responses)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd TBB

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r python_ai/requirements.txt

# Create directories
mkdir -p python_ai/data python_ai/logs

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the Server

```bash
# Option 1: Manual start
cd python_ai
python main.py

# Option 2: Quick start script
./START_SMS_BOT.sh
```

Server runs on: http://localhost:8000

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Send test message
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "testuser", "message": "I feel anxious"}'

# Verify setup
python test_twilio_setup.py

# API documentation
open http://localhost:8000/docs
```

---

## 🏗 Architecture

```
User texts phone number
        ↓
    Twilio SMS Gateway
        ↓
    FastAPI Backend (/sms/webhook)
        ↓
    Rate Limiting (30 msg/hour)
        ↓
    Crisis Detection
    ├─ Crisis? → Immediate intervention
    └─ Safe → Continue
        ↓
    Semantic Routing (MoE)
    ├─ CBT Expert
    ├─ Mindfulness Expert
    └─ Motivation Expert
        ↓
    Load Conversation History
        ↓
    Claude AI + Expert Prompts
        ↓
    Event Extraction
    ├─ Important dates → Schedule follow-ups
    └─ Continue
        ↓
    Personalization (adapt style)
        ↓
    Save to Database
        ↓
    Send SMS Response
        ↓
    User receives message
```

**Background Scheduler:**
- Runs every minute
- Checks for scheduled messages
- Sends proactive check-ins

---

## 📂 Project Structure

```
TBB/
├── python_ai/                    # Main application
│   ├── main.py                   # FastAPI app + endpoints
│   ├── config.py                 # Configuration
│   ├── database.py               # SQLAlchemy models
│   ├── safety.py                 # Crisis detection
│   ├── routers.py                # Semantic routing (MoE)
│   ├── sms_handler.py            # Twilio integration
│   ├── firebase_auth.py          # Firebase phone auth
│   ├── scheduler.py              # Proactive messaging
│   ├── event_extraction.py       # Extract important dates
│   ├── personalization.py        # Style learning
│   │
│   ├── experts/                  # Therapy experts
│   │   ├── cbt_expert.py
│   │   ├── mindfulness_expert.py
│   │   ├── motivation_expert.py
│   │   └── claude_expert.py
│   │
│   ├── memory/                   # Conversation memory
│   │   └── conversation.py
│   │
│   └── requirements.txt
│
├── SYSTEM_DESIGN.md              # Technical architecture
├── PRODUCT_REQUIREMENTS.md       # Product specs
├── TEAM_HANDOFF.md              # Developer onboarding
├── TWILIO_SETUP_CHECKLIST.md   # SMS setup
├── FIREBASE_SETUP_GUIDE.md      # Phone auth setup
├── START_SMS_BOT.sh             # Quick start script
├── test_twilio_setup.py         # Setup verification
│
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## 🔑 Key Features Explained

### 1. Crisis Detection
Every message is scanned for concerning keywords:
- Suicide ideation
- Self-harm
- Harm to others
- Abuse
- Substance abuse

**Response:**
- Immediate intervention message
- Crisis resources provided (988 Suicide Lifeline)
- Incident logged for review
- User flagged for follow-up

### 2. Semantic Routing (Mixture of Experts)
Messages are routed to specialized experts using semantic similarity:

```python
"I can't stop worrying" → Mindfulness Expert (0.85 confidence)
"I keep thinking I'm not good enough" → CBT Expert (0.92 confidence)
"I can't get motivated to study" → Motivation Expert (0.88 confidence)
```

### 3. Event Tracking & Proactive Outreach
AI extracts important dates from conversation:

**Example:**
```
User: "I have an exam on Friday"
Bot: "Let's work on that exam stress...
     I'll check in with you before your exam!"

[Thursday 9 AM]
Bot: "Your exam is tomorrow! How's your prep going?"

[Saturday]
Bot: "How did your exam go?"
```

### 4. Conversation Memory
- Stores all messages with timestamps
- Retrieves context for relevant responses
- Tracks conversation metrics
- No need to repeat yourself

### 5. Personalization
Learns and adapts to user's style:
- Message length preferences
- Formality level
- Emoji usage
- Response timing

---

## 🗄 Database Schema

**users** - User profiles (phone numbers, preferences)
**messages** - Conversation history
**safety_incidents** - Crisis events and interventions
**important_events** - User's important dates
**scheduled_messages** - Proactive outreach queue

See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for complete schema.

---

## 🔌 API Endpoints

### POST `/sms/webhook`
Receives incoming SMS from Twilio

### POST `/message`
Send message to bot (API access)

### POST `/auth/verify-phone`
Verify phone number via Firebase

### GET `/health`
Health check for monitoring

### GET `/stats/{user_id}`
User statistics and analytics

**Full API docs:** http://localhost:8000/docs

---

## 🛠 Technology Stack

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM with async support
- **SQLite** - Database (dev), PostgreSQL (prod)
- **Uvicorn** - ASGI server

### AI/ML
- **Claude** - Anthropic LLM (Sonnet 4.5)
- **Sentence Transformers** - Semantic embeddings
- **scikit-learn** - Cosine similarity

### Communication
- **Twilio** - SMS gateway
- **Firebase** - Phone authentication (optional)

### Infrastructure
- **APScheduler** - Background job scheduling
- **Python-dotenv** - Environment management
- **JSON Logger** - Structured logging

---

## 🧪 Testing

### Automated Tests
```bash
pytest python_ai/tests/
```

### Manual Testing
```bash
# Test crisis detection
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "test", "message": "I want to hurt myself"}'

# Test routing
curl -X POST "http://localhost:8000/test-routing?message=I%20feel%20anxious"

# Simulate Twilio webhook
curl -X POST http://localhost:8000/sms/webhook \
  -d "From=+15551234567" \
  -d "Body=I need help with stress"
```

### Setup Verification
```bash
python test_twilio_setup.py
```

---

## 📊 Monitoring

### Logs
```bash
# Real-time logs
tail -f python_ai/logs/therapy_bot.log

# Error search
grep ERROR python_ai/logs/therapy_bot.log
```

### Database
```bash
sqlite3 python_ai/data/users.db

# View users
SELECT * FROM users;

# Recent messages
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;

# Crisis incidents
SELECT * FROM safety_incidents WHERE resolved = 0;
```

### Metrics
- Response time
- Error rate
- Daily active users
- Crisis incidents
- SMS costs
- API token usage

---

## 🚨 Important Safety Notes

**This is a demonstration project, NOT production medical software.**

**Required for production:**
- [ ] Licensed clinician oversight
- [ ] HIPAA compliance (BAA with vendors)
- [ ] Human crisis counselor integration
- [ ] Advanced ML-based crisis detection
- [ ] Comprehensive testing and validation
- [ ] Legal review and liability insurance

**Current safety features:**
- Crisis keyword detection
- Immediate resource provision (988 Lifeline)
- Incident logging and user flagging
- Rate limiting
- Audit trails

---

## 🚀 Deployment

### Development
```bash
python main.py
```

### Staging (Docker)
```bash
docker build -t tbb-bot:staging .
docker run -p 8000:8000 --env-file .env tbb-bot:staging
```

### Production
See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for:
- AWS/GCP deployment guides
- Scaling strategies
- Cost estimates
- Monitoring setup

---

## 📈 Roadmap

### Phase 1: MVP (✅ Complete)
- [x] SMS chatbot
- [x] Crisis detection
- [x] Semantic routing
- [x] Conversation memory
- [x] Event tracking
- [x] Proactive outreach
- [x] Personalization

### Phase 2: Enhanced Features (3-6 months)
- [ ] Voice call support
- [ ] Multi-language (Spanish, Mandarin)
- [ ] Therapist dashboard
- [ ] User feedback system
- [ ] Group sessions
- [ ] Advanced analytics

### Phase 3: Platform (6-12 months)
- [ ] White-label solution
- [ ] EHR integration
- [ ] Insurance billing
- [ ] Video sessions
- [ ] Clinical trials support

---

## 💰 Cost Breakdown

### MVP (100 users)
- Hosting: $25/month
- Database: $15/month
- Twilio SMS: $8/month (1,000 messages)
- Claude API: $10/month
- **Total: ~$60/month**

### Production (10,000 users)
- Infrastructure: $500/month
- Twilio SMS: $800/month (100k messages)
- Claude API: $1,000/month
- **Total: ~$2,900/month**

**Per-user cost: ~$0.23/month**

See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for detailed breakdown.

---

## 🤝 Contributing

1. Read [TEAM_HANDOFF.md](TEAM_HANDOFF.md) for onboarding
2. Check [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md) for roadmap
3. Review [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for architecture
4. Follow code standards (PEP 8, type hints, docstrings)
5. Write tests for new features
6. Submit PR with clear description

---

## 📞 Support

### Crisis Resources
- 🇺🇸 **988 Suicide & Crisis Lifeline** - Call/text **988**
- 🇺🇸 **Crisis Text Line** - Text **HELLO** to **741741**
- 🌍 **International** - [findahelpline.com](https://findahelpline.com/)

### Technical Support
- **Documentation:** See docs above
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Questions:** See TEAM_HANDOFF.md for contacts

---

## 📄 License

[TBD - Add license]

---

## 🙏 Acknowledgments

Built with care for mental health awareness.

Special thanks to:
- Anthropic (Claude AI)
- Twilio (SMS infrastructure)
- Open source community

---

**Remember:** This is healthcare software. Every line of code could help someone in crisis. Test thoroughly, code compassionately, and prioritize safety above all else.

**Let's build something that helps people.** 💙
