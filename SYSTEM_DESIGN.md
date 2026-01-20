# TBB Therapy Bot - System Design Document

## Executive Summary

**Project:** AI-powered therapy chatbot accessible via SMS
**Current Status:** MVP complete, ready for scale
**Technology:** Python, FastAPI, SQLite, Claude AI, Twilio, Firebase
**Target Users:** Anyone with a phone number (no app required)

---

## 1. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER LAYER                           │
│  (SMS via any mobile phone - no app installation required)  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMMUNICATION LAYER                       │
│                                                              │
│  ┌──────────────┐              ┌──────────────┐           │
│  │   Twilio     │              │   Firebase   │           │
│  │  SMS Gateway │              │  Phone Auth  │           │
│  └──────────────┘              └──────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend Server                     │ │
│  │                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │   Webhook    │  │  REST API    │  │  CORS       │ │ │
│  │  │   Handler    │  │  Endpoints   │  │  Middleware │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Business Logic Layer                       │ │
│  │                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │   Crisis     │  │   Semantic   │  │   Expert    │ │ │
│  │  │  Detection   │  │   Router     │  │   System    │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  │                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │Conversation  │  │ Event        │  │Personali-   │ │ │
│  │  │  Memory      │  │ Extraction   │  │  zation     │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
│                                                              │
│  ┌──────────────┐              ┌──────────────┐           │
│  │  Claude AI   │              │  Embedding   │           │
│  │    (LLM)     │              │    Models    │           │
│  └──────────────┘              └──────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   SQLite Database                       │ │
│  │  (Development - PostgreSQL recommended for production)  │ │
│  │                                                         │ │
│  │  • Users            • Important Events                 │ │
│  │  • Messages         • Scheduled Messages               │ │
│  │  • Safety Incidents                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Background Job Scheduler                   │ │
│  │         (APScheduler - Proactive Outreach)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:**
  - Development: SQLite with async support (aiosqlite)
  - Production: PostgreSQL recommended
- **ORM:** SQLAlchemy 2.0 (async)
- **API Documentation:** Auto-generated OpenAPI/Swagger

### AI/ML
- **LLM:** Claude (Anthropic) - Sonnet 4.5
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Operations:** scikit-learn (cosine similarity)
- **Routing:** Semantic routing via embeddings

### Communication
- **SMS Gateway:** Twilio
- **Phone Auth:** Firebase Phone Authentication
- **Webhook Processing:** FastAPI async endpoints

### Infrastructure
- **Scheduling:** APScheduler (proactive messages)
- **Logging:** Python JSON Logger
- **Environment:** python-dotenv
- **ASGI Server:** Uvicorn

### Dependencies (key packages)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
twilio==8.10.0
firebase-admin==6.3.0
anthropic==0.40.0
sentence-transformers>=2.2.2
apscheduler==3.10.4
```

---

## 3. Core Components

### 3.1 Crisis Detection System

**Purpose:** Identify and respond to mental health emergencies

**Detection Categories:**
- Suicide ideation
- Self-harm
- Harm to others
- Abuse (physical, sexual, emotional)
- Substance abuse

**Workflow:**
1. Every incoming message scanned for crisis keywords
2. Keyword matching with severity scoring
3. Immediate intervention response generated
4. Safety incident logged to database
5. User flagged for follow-up
6. Optional: Alert sent to crisis hotline email

**Database Schema:**
```python
SafetyIncident:
  - id (primary key)
  - user_id (foreign key)
  - message_id (foreign key)
  - incident_type (enum)
  - severity (low/medium/high/critical)
  - detected_keywords (JSON)
  - action_taken (text)
  - resolved (boolean)
  - timestamp
```

---

### 3.2 Semantic Routing (Mixture of Experts)

**Purpose:** Route messages to appropriate therapy expert

**Experts:**
1. **CBT Expert** - Cognitive Behavioral Therapy
   - Thought patterns, cognitive distortions
   - Behavioral activation
   - Problem-solving

2. **Mindfulness Expert**
   - Breathing exercises
   - Meditation techniques
   - Present-moment awareness

3. **Motivation Expert**
   - Goal setting
   - Progress celebration
   - Encouragement

**Routing Algorithm:**
```python
1. Generate embedding for user message
2. Calculate cosine similarity with expert prototypes
3. Select expert with highest similarity (confidence > threshold)
4. Fall back to general expert if no clear match
5. Log routing decision and confidence score
```

**Advantages:**
- Specialized responses
- Expertise-driven conversations
- Better user experience than generic chatbot

---

### 3.3 Conversation Memory

**Purpose:** Maintain context across sessions

**Implementation:**
- Store all messages in database with timestamps
- Retrieve sliding window of recent messages (default: 10)
- Format as chat history for LLM context
- Track conversation metrics (length, topics, sentiment)

**Memory Retrieval:**
```python
async def get_conversation_history(user_id, limit=10):
    # Fetch last N messages
    # Return in chronological order
    # Include role (user/assistant) and content
```

**Context Window Management:**
- Recent messages prioritized
- Summarization for long conversations
- Important events flagged and retained

---

### 3.4 Event Tracking & Proactive Outreach

**Purpose:** Remember important dates and follow up

**Features:**
1. **Event Extraction:** AI identifies important dates from conversation
   - Tests, exams
   - Appointments
   - Deadlines
   - Social events

2. **Scheduled Follow-ups:**
   - Pre-event check-ins (e.g., 3 days before)
   - Post-event follow-ups (e.g., 1 day after)
   - Customizable timing

3. **Background Scheduler:**
   - APScheduler runs every minute
   - Checks for due messages
   - Sends via SMS automatically

**Database Schema:**
```python
ImportantEvent:
  - id
  - user_id
  - event_type (test, appointment, deadline, social, other)
  - description
  - event_date
  - importance (low/medium/high)
  - follow_up_before_days (CSV: "3,7")
  - follow_up_after_days (CSV: "1,3")
  - completed
  - created_at

ScheduledMessage:
  - id
  - user_id
  - related_event_id
  - message_content
  - message_type (follow_up, check_in, reminder, motivation)
  - scheduled_time
  - sent (boolean)
  - sent_at
  - created_at
```

---

### 3.5 Personalization Engine

**Purpose:** Adapt to user's communication style

**Learning Signals:**
- Message length preferences
- Formality level
- Emoji usage
- Response timing

**Storage:**
```python
User.communication_style (JSON):
{
  "formality": "casual",
  "preferred_length": "medium",
  "emoji_frequency": "moderate",
  "topics_of_interest": ["anxiety", "sleep"]
}
```

**Adaptation:**
- Analyze last N messages (default: 50)
- Update style profile
- Inject style preferences into LLM prompts

---

## 4. API Endpoints

### Public Endpoints

#### `POST /sms/webhook`
**Purpose:** Receive incoming SMS from Twilio
**Request:**
```json
{
  "From": "+15551234567",
  "Body": "I'm feeling anxious",
  "MessageSid": "SM123..."
}
```
**Response:** TwiML (Twilio Markup Language)
**Flow:**
1. Extract phone number and message
2. Run crisis detection
3. Route to appropriate expert
4. Generate response
5. Save conversation history
6. Send SMS via Twilio

---

#### `POST /auth/verify-phone`
**Purpose:** Verify phone number via Firebase
**Request:**
```json
{
  "id_token": "eyJhbGci..."
}
```
**Response:**
```json
{
  "success": true,
  "phone_number": "+15551234567",
  "user_id": "+15551234567",
  "message": "Phone number verified successfully"
}
```

---

#### `POST /message`
**Purpose:** Send message to bot (API/web interface)
**Request:**
```json
{
  "user": "+15551234567",
  "message": "I need help with anxiety"
}
```
**Response:**
```json
{
  "reply": "I understand you're experiencing anxiety...",
  "expert_used": "cbt",
  "routing_confidence": 0.89,
  "crisis_detected": false
}
```

---

#### `GET /health`
**Purpose:** Health check for monitoring
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "crisis_detection": true
}
```

---

#### `GET /stats/{user_id}`
**Purpose:** User statistics and analytics
**Response:**
```json
{
  "user_id": "+15551234567",
  "total_messages": 42,
  "is_flagged": false,
  "recent_activity": {
    "messages_last_hour": 3,
    "last_message_time": "2025-01-20T10:30:00Z"
  },
  "conversation_preview": [...]
}
```

---

## 5. Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │◄─────┐
│ user_id (UQ)    │      │
│ created_at      │      │
│ last_active     │      │
│ message_count   │      │
│ is_flagged      │      │
│ preferred_expert│      │
│ comm_style (JSON)│     │
└─────────────────┘      │
         ▲               │
         │               │
         │ 1:N           │ 1:N
         │               │
┌────────┴────────┐ ┌────┴──────────────┐
│    Message      │ │  SafetyIncident   │
│─────────────────│ │───────────────────│
│ id (PK)         │ │ id (PK)           │
│ user_id (FK)    │ │ user_id (FK)      │
│ role            │ │ message_id (FK)   │
│ content         │ │ incident_type     │
│ expert_used     │ │ severity          │
│ timestamp       │ │ detected_keywords │
└─────────────────┘ │ action_taken      │
                    │ resolved          │
                    │ timestamp         │
                    └───────────────────┘

┌─────────────────────┐
│  ImportantEvent     │
│─────────────────────│
│ id (PK)             │◄──┐
│ user_id (FK)        │   │
│ event_type          │   │ 1:N
│ description         │   │
│ event_date          │   │
│ importance          │   │
│ follow_up_before    │   │
│ follow_up_after     │   │
│ completed           │   │
└─────────────────────┘   │
                          │
                ┌─────────┴────────┐
                │ ScheduledMessage │
                │──────────────────│
                │ id (PK)          │
                │ user_id (FK)     │
                │ related_event_id │
                │ message_content  │
                │ message_type     │
                │ scheduled_time   │
                │ sent             │
                │ sent_at          │
                └──────────────────┘
```

### Indexes

**Performance-critical indexes:**
```sql
-- User lookups
CREATE INDEX idx_user_user_id ON users(user_id);

-- Message retrieval
CREATE INDEX idx_message_user_timestamp ON messages(user_id, timestamp DESC);

-- Safety incidents
CREATE INDEX idx_safety_user ON safety_incidents(user_id);
CREATE INDEX idx_safety_timestamp ON safety_incidents(timestamp DESC);

-- Event tracking
CREATE INDEX idx_event_user ON important_events(user_id);
CREATE INDEX idx_event_date ON important_events(event_date);

-- Scheduled messages
CREATE INDEX idx_scheduled_unsent ON scheduled_messages(scheduled_time, sent);
CREATE INDEX idx_scheduled_user ON scheduled_messages(user_id);
```

---

## 6. Data Flow

### Incoming SMS Flow

```
1. User sends SMS to Twilio number
        ↓
2. Twilio receives SMS
        ↓
3. Twilio POST to /sms/webhook
        ↓
4. FastAPI receives webhook
        ↓
5. Extract: phone_number, message_text
        ↓
6. Get or create user (database lookup)
        ↓
7. Check rate limit (30 msg/hour default)
        ↓
8. CRISIS DETECTION
   ├─ Crisis detected? → Generate crisis response
   └─ No crisis → Continue to routing
        ↓
9. SEMANTIC ROUTING
   ├─ Generate message embedding
   ├─ Calculate similarity with expert prototypes
   └─ Select best expert (CBT/Mindfulness/Motivation)
        ↓
10. Load conversation history (last 10 messages)
        ↓
11. Generate context summary (recent topics)
        ↓
12. Call LLM (Claude) with:
    ├─ Expert system prompt
    ├─ Conversation history
    ├─ User's communication style
    └─ Current message
        ↓
13. Receive LLM response
        ↓
14. Extract important events (if any)
    └─ Create ImportantEvent records
    └─ Schedule follow-up messages
        ↓
15. Save message pair to database:
    ├─ User message (role: user)
    └─ Bot response (role: assistant)
        ↓
16. Update user metadata:
    ├─ last_active timestamp
    ├─ message_count++
    └─ communication_style (if needed)
        ↓
17. Format response for SMS (160-1600 chars)
        ↓
18. Send via Twilio SMS API
        ↓
19. Return TwiML response to Twilio
        ↓
20. User receives SMS
```

### Proactive Outreach Flow

```
1. APScheduler runs every 1 minute
        ↓
2. Query scheduled_messages WHERE:
   ├─ sent = false
   └─ scheduled_time <= NOW()
        ↓
3. For each pending message:
        ↓
4. Load user information
        ↓
5. Format message content
        ↓
6. Send via Twilio SMS
        ↓
7. Update ScheduledMessage:
   ├─ sent = true
   └─ sent_at = NOW()
        ↓
8. Log delivery status
```

---

## 7. Security Considerations

### Data Privacy
- **PII Protection:** Phone numbers are the only PII stored
- **Encryption:**
  - Transport: TLS 1.3 for all API calls
  - At rest: Database encryption recommended
- **HIPAA Compliance:**
  - All conversations are healthcare-related
  - Requires Business Associate Agreement with hosting provider
  - Audit logging of all data access

### Authentication
- **SMS Users:** Phone number verified via Twilio
- **API Users:** Firebase ID token verification
- **Webhook Security:** Twilio signature validation

### Rate Limiting
- **Default:** 30 messages/hour per user
- **Purpose:** Prevent abuse, manage costs
- **Implementation:** Track message_count and last_active

### Crisis Response
- **Mandatory Reporting:** Safety incidents logged permanently
- **Audit Trail:** All crisis responses tracked
- **Emergency Contact:** Crisis hotline number provided (988)

---

## 8. Scaling Strategy

### Current State (MVP)
- **Architecture:** Monolithic FastAPI app
- **Database:** SQLite (single file)
- **Hosting:** Single server
- **Capacity:** ~100 concurrent users

### Phase 1: Small Scale (100-1,000 users)
**Changes:**
- Migrate to PostgreSQL
- Deploy to cloud (AWS/GCP/Heroku)
- Add Redis for caching
- Horizontal scaling with load balancer

**Infrastructure:**
```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┬───────┐
   │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│App 1│ │App 2│ │App 3│
└──┬──┘ └──┬──┘ └──┬──┘
   │       │       │
   └───┬───┴───┬───┘
       │       │
   ┌───▼───────▼───┐
   │  PostgreSQL   │
   └───────────────┘
```

**Estimated Costs:**
- Servers: $50-100/month
- Database: $30/month
- Twilio: $0.0079/SMS (~$80/month for 10k messages)
- Claude API: $3-15/million tokens (~$50-200/month)

---

### Phase 2: Medium Scale (1,000-10,000 users)
**Changes:**
- Microservices architecture
- Separate services:
  - API Gateway
  - Message Processor
  - AI/LLM Service
  - Scheduler Service
- Message queue (RabbitMQ/SQS)
- Database read replicas

**Infrastructure:**
```
                ┌──────────────┐
                │ Load Balancer│
                └──────┬───────┘
                       │
           ┌───────────┼───────────┐
           │           │           │
    ┌──────▼─────┐ ┌──▼────┐ ┌────▼────┐
    │ API Gateway│ │ Web UI│ │Scheduler│
    └──────┬─────┘ └───────┘ └────┬────┘
           │                       │
           │    ┌──────────────────┘
           │    │
      ┌────▼────▼─────┐
      │ Message Queue  │
      └────┬─────┬─────┘
           │     │
    ┌──────▼─┐ ┌▼───────────┐
    │Message │ │ AI Service │
    │Process │ └┬───────────┘
    └────┬───┘  │
         │      │
    ┌────▼──────▼────┐
    │   PostgreSQL   │
    │  (Primary +    │
    │   Replicas)    │
    └────────────────┘
```

**Estimated Costs:**
- Infrastructure: $500-1,000/month
- Twilio: $800/month (100k messages)
- Claude API: $500-2,000/month
- **Total:** ~$2,000-4,000/month

---

### Phase 3: Large Scale (10,000+ users)
**Changes:**
- Multi-region deployment
- CDN for static assets
- Database sharding by user_id
- Auto-scaling groups
- Caching layer (Redis/Memcached)
- Observability: DataDog, Sentry
- A/B testing framework

**Advanced Features:**
- Voice call support (Twilio Voice)
- Multi-language support
- Advanced analytics dashboard
- Machine learning for routing optimization
- Predictive crisis detection

**Infrastructure:**
- Kubernetes orchestration
- Managed database services
- Serverless functions for spikes
- Multi-AZ redundancy

**Estimated Costs:**
- Infrastructure: $3,000-10,000/month
- SMS/Voice: $5,000+/month
- AI/ML: $2,000-10,000/month
- **Total:** $10,000-30,000/month for 100k+ users

---

## 9. Deployment Architecture

### Development Environment
```bash
# Local machine
├── SQLite database (./data/users.db)
├── ngrok tunnel (for Twilio webhooks)
└── Python virtual environment
```

### Staging Environment
```
AWS/GCP:
├── EC2/Compute Engine instance
├── RDS PostgreSQL (small instance)
├── Elastic IP / Static IP
└── HTTPS with Let's Encrypt
```

### Production Environment
```
AWS Example:
├── Route 53 (DNS)
├── CloudFront (CDN)
├── ALB (Application Load Balancer)
├── ECS/EKS (Container orchestration)
│   ├── API Service (3+ replicas)
│   ├── Message Processor (2+ replicas)
│   └── Scheduler Service (1 replica)
├── RDS PostgreSQL (Multi-AZ)
├── ElastiCache Redis
├── S3 (file storage)
├── CloudWatch (monitoring)
└── Secrets Manager (credentials)
```

---

## 10. Monitoring & Observability

### Key Metrics

**Business Metrics:**
- Daily Active Users (DAU)
- Messages sent/received per day
- Crisis incidents detected per day
- Average response time
- User retention (7-day, 30-day)

**Technical Metrics:**
- API latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query performance
- LLM token usage
- SMS delivery rate

**Cost Metrics:**
- Twilio costs per day
- Claude API costs per day
- Infrastructure costs per day

### Alerting

**Critical Alerts:**
- Service down (> 1 minute)
- Error rate > 5%
- Database connection failure
- Twilio webhook failures

**Warning Alerts:**
- Response time > 3 seconds (p95)
- Crisis incidents spike (> 2x normal)
- Database disk > 80%
- Memory usage > 85%

### Logging

**Structured Logging:**
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "level": "INFO",
  "service": "message_processor",
  "user_id": "+15551234567",
  "event": "message_received",
  "expert_used": "cbt",
  "response_time_ms": 234,
  "crisis_detected": false
}
```

**Log Retention:**
- Application logs: 30 days
- Audit logs: 7 years (HIPAA requirement)
- Error logs: 90 days

---

## 11. Testing Strategy

### Unit Tests
- Individual functions and methods
- Mock external dependencies (Twilio, Claude AI)
- Coverage target: > 80%

### Integration Tests
- API endpoint testing
- Database operations
- Webhook processing
- Crisis detection system

### End-to-End Tests
- Full SMS flow simulation
- Proactive message delivery
- Event extraction and scheduling

### Load Testing
- Apache JMeter or Locust
- Simulate 100/1000/10000 concurrent users
- Measure response times and error rates

### Security Testing
- OWASP Top 10 vulnerabilities
- Penetration testing
- SQL injection prevention
- XSS/CSRF protection

---

## 12. Development Roadmap

### Phase 1: MVP (Complete ✅)
- [x] Basic SMS chatbot
- [x] Crisis detection
- [x] Semantic routing
- [x] Conversation memory
- [x] Event tracking
- [x] Proactive outreach

### Phase 2: Enhanced Features (3-6 months)
- [ ] Multi-language support (Spanish, Mandarin)
- [ ] Voice call support
- [ ] Group therapy sessions
- [ ] Therapist dashboard (moderation)
- [ ] Advanced analytics
- [ ] User feedback system

### Phase 3: Platform (6-12 months)
- [ ] White-label solution
- [ ] Customizable therapy approaches
- [ ] Integration with EHR systems
- [ ] Teletherapy scheduling
- [ ] Video session support
- [ ] Insurance billing integration

### Phase 4: Scale (12+ months)
- [ ] Multi-region deployment
- [ ] Advanced ML models
- [ ] Predictive analytics
- [ ] Research partnerships
- [ ] Clinical trials integration

---

## 13. Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM hallucination gives bad advice | Medium | High | Human review, safety filters, disclaimers |
| Twilio service outage | Low | High | Multi-provider strategy, fallback SMS |
| Database corruption | Low | High | Daily backups, point-in-time recovery |
| DDoS attack | Medium | Medium | Rate limiting, CloudFlare, WAF |
| API key leak | Low | High | Secrets management, rotation policy |

### Compliance Risks

| Risk | Mitigation |
|------|------------|
| HIPAA violation | BAA with vendors, encryption, audit logs |
| Data breach | Encryption, access controls, incident response plan |
| Mandatory reporting failure | Automated crisis alerts, human oversight |
| Patient safety incident | Clear disclaimers, crisis hotline integration |

### Business Risks

| Risk | Mitigation |
|------|------------|
| High SMS costs | Optimize message length, smart scheduling |
| Low user retention | Personalization, value-add features |
| Regulatory changes | Legal counsel, compliance monitoring |
| Competition | Unique features, superior UX, clinical validation |

---

## 14. Cost Breakdown

### MVP Costs (100 users)
```
Hosting (Heroku/Railway):     $25/month
Database (managed Postgres):  $15/month
Twilio (1,000 SMS/month):     $8/month
Claude API (~100k tokens):    $10/month
Domain + SSL:                 $2/month
───────────────────────────────────────
Total:                        $60/month
```

### Small Scale (1,000 users)
```
Hosting (AWS EC2 t3.medium):  $50/month
Database (RDS db.t3.small):   $30/month
Twilio (10,000 SMS/month):    $80/month
Claude API (~1M tokens):      $100/month
Monitoring (DataDog):         $15/month
───────────────────────────────────────
Total:                        $275/month
```

### Medium Scale (10,000 users)
```
Compute (ECS):                $500/month
Database (RDS multi-AZ):      $300/month
Cache (ElastiCache):          $100/month
Twilio (100k SMS/month):      $800/month
Claude API (~10M tokens):     $1,000/month
CDN + Storage:                $50/month
Monitoring:                   $150/month
───────────────────────────────────────
Total:                        $2,900/month
```

### Per-User Economics
- SMS cost: ~$0.08/user/month (10 messages)
- AI cost: ~$0.10/user/month
- Infrastructure: ~$0.05/user/month (at scale)
- **Total:** ~$0.23/user/month

**Revenue Model Options:**
- Freemium: Free basic, $9.99/month premium
- B2B: License to healthcare providers ($5-10/user/month)
- Insurance: Covered mental health benefit

---

## 15. Team Structure Recommendations

### Phase 1: MVP Team (3-4 people)
- **1 Full-Stack Engineer:** API, database, integrations
- **1 AI/ML Engineer:** LLM integration, routing, embeddings
- **1 Product Manager:** Requirements, user testing
- **1 Designer (part-time):** SMS flow, future web UI

### Phase 2: Growth Team (8-10 people)
- **2 Backend Engineers:** Core services, APIs
- **1 Frontend Engineer:** Dashboard, web interface
- **1 AI/ML Engineer:** Advanced models, optimization
- **1 DevOps Engineer:** Infrastructure, deployment, monitoring
- **1 QA Engineer:** Testing, quality assurance
- **1 Product Manager:** Roadmap, prioritization
- **1 Designer:** UX/UI, user research
- **1 Clinical Advisor (contractor):** Safety, therapy quality

### Phase 3: Scale Team (20+ people)
**Engineering (12-15):**
- Backend team (4-5)
- Frontend team (2-3)
- ML/AI team (2-3)
- DevOps/SRE (2)
- Mobile team (2) [if building apps]
- QA/Test (2)

**Product (3-4):**
- Product Manager
- Product Designer
- UX Researcher
- Data Analyst

**Operations (3-4):**
- Customer Success
- Clinical Oversight
- Compliance/Legal
- Community Management

**Leadership:**
- CTO
- Head of Product
- Clinical Director

---

## 16. Key Differentiators

### What Makes This Unique?

1. **SMS-First Approach**
   - No app download required
   - Universal accessibility (any phone)
   - Lower barrier to entry than apps

2. **Proactive Outreach**
   - AI remembers important dates
   - Checks in before/after events
   - Feels like a caring friend

3. **Specialized Experts**
   - Not one-size-fits-all
   - CBT, mindfulness, motivation approaches
   - Better outcomes than generic chatbots

4. **Crisis Detection**
   - Real-time safety monitoring
   - Immediate intervention
   - Potential to save lives

5. **Conversation Memory**
   - Remembers everything
   - No need to repeat yourself
   - Builds real relationship

---

## 17. Success Metrics

### User Engagement
- **Target:** 60% weekly retention
- **Target:** 10 messages/user/week average
- **Target:** < 24 hour response time to proactive messages

### Clinical Outcomes
- **Target:** 70% of users report improvement (self-reported)
- **Target:** 50% reduction in crisis escalations over 30 days
- **Target:** 80% user satisfaction score

### Technical Performance
- **Target:** 99.9% uptime
- **Target:** < 2 second average response time
- **Target:** < 1% error rate

### Business Metrics
- **Target:** < $5 customer acquisition cost
- **Target:** < 20% monthly churn
- **Target:** $0.50/user/month contribution margin

---

## Conclusion

This system is production-ready at the MVP level and designed for scale. The architecture is modular, the code is clean, and the foundation is solid.

**Next Steps:**
1. Complete Twilio verification
2. Deploy to staging environment
3. Conduct beta testing with 10-50 users
4. Gather feedback and iterate
5. Plan production launch

The technology is proven, the need is real, and the timing is right. Let's build something that helps people.

---

**Document Version:** 1.0
**Last Updated:** January 20, 2025
**Author:** TBB Technical Team
