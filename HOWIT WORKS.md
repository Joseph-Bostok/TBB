# How Your SMS Therapy Bot Works

## 🎯 The Big Picture

```
YOU (text) → TWILIO → YOUR SERVER → BOT BRAIN → TWILIO → YOU (reply)
                          ↓
                      DATABASE
                     (remembers)
```

---

## 📱 Example: "I have a test on Friday"

Let's trace EXACTLY what happens when you text this:

### Step 1: You Send SMS
```
Your Phone → Twilio Number (+1234567890)
Message: "I have a test on Friday and I'm stressed"
```

### Step 2: Twilio Receives It
```
Twilio receives SMS
Twilio makes HTTP POST request to your server:
URL: https://your-server.com/sms/webhook
Data: {
  "From": "+19804060024",
  "Body": "I have a test on Friday and I'm stressed"
}
```

### Step 3: Your Server Receives It (main.py)
```python
# File: python_ai/main.py
# Line: 518 - /sms/webhook endpoint

@app.post("/sms/webhook")
async def sms_webhook(From, Body, ...):
    # Twilio just called this!
    # From = "+19804060024"
    # Body = "I have a test on Friday and I'm stressed"
```

### Step 4: Crisis Check (safety.py)
```python
# File: python_ai/safety.py
# Checks for: suicide, self-harm, abuse

is_crisis = detect_crisis("I have a test...")
# Result: False (no crisis detected)
# If true: immediately send 988 hotline info
```

### Step 5: Event Extraction (event_extraction.py)
```python
# File: python_ai/event_extraction.py
# Line: 73 - extract_events()

events = extract_events("I have a test on Friday...")
# Finds:
# - Pattern: "test"
# - Date: "Friday" → converts to actual date
# Result: {
#   "type": "test",
#   "date": datetime(2025, 11, 14),  # This Friday
#   "importance": "high"
# }

# Saves to database:
# Table: important_events
# Row: user_id=1, type="test", date=2025-11-14
```

### Step 6: Routing (routers.py)
```python
# File: python_ai/routers.py
# Line: 89 - route()

expert, confidence = route("I have a test on Friday and I'm stressed")
# Uses AI to analyze message:
# - "test" + "stressed" → anxiety related
# Result: expert="cbt", confidence=0.85
```

### Step 7: Expert Response (cbt_expert.py)
```python
# File: python_ai/experts/cbt_expert.py
# Line: 42 - generate_response()

response = cbt_expert.generate_response(
    "I have a test on Friday and I'm stressed",
    conversation_history=[...],
    context={...}
)
# Generates therapeutic response about test anxiety
# Result: "I hear you're feeling stressed about your test..."
```

### Step 8: Personalization (personalization.py)
```python
# File: python_ai/personalization.py
# Line: 193 - adapt_response()

# Analyzes YOUR style from past messages:
user_style = {
    "formality": "casual",  # You say "hey" not "hello"
    "avg_message_length": 30,  # You write short texts
    "uses_emojis": False  # You don't use emojis
}

# Adapts bot response to match YOUR style
adapted = adapt_response(response, user_style)
# Makes it shorter, more casual, no emojis
```

### Step 9: Add Event Note
```python
# File: python_ai/main.py
# Line: 393

if events:
    response += "\n\nI've made a note about your test on Friday. I'll check in with you about it!"
```

### Step 10: Send SMS Response (sms_handler.py)
```python
# File: python_ai/sms_handler.py
# Line: 47 - send_sms()

success = send_sms(
    to_number="+19804060024",
    message="I hear you're stressed...I've made a note about your test on Friday!"
)
# Uses Twilio API to send SMS back to you
```

### Step 11: You Receive Reply
```
Your Phone receives SMS:
"I hear you're feeling stressed about your test. Test anxiety is common...

I've made a note about your test on Friday. I'll check in with you about it!"
```

### Step 12: Save to Database (database.py)
```python
# File: python_ai/database.py
# Saves to SQLite database:

# Table: messages
# - user_id: 1
# - role: "user"
# - content: "I have a test on Friday..."
# - timestamp: 2025-11-10 18:30:00

# Table: messages
# - user_id: 1
# - role: "assistant"
# - content: "I hear you're feeling stressed..."
# - expert_used: "cbt"
# - timestamp: 2025-11-10 18:30:02
```

---

## ⏰ Background: Proactive Scheduler

WHILE you're studying, the scheduler is working in the background...

### Thursday 9 AM (Day Before Test)
```python
# File: python_ai/scheduler.py
# Runs every minute checking:

scheduled_messages = get_messages_due()
# Finds message scheduled for Thursday 9 AM:
# "Hi! Your test is tomorrow. How's your preparation going?"

send_sms("+19804060024", "Hi! Your test is tomorrow...")
```

You receive text Thursday morning!

### Saturday 9 AM (Day After Test)
```python
# Scheduler sends another follow-up:
"How did your test go? I'd love to hear about it!"
```

You receive text Saturday morning!

---

## 📂 File Roles - Restaurant Analogy

Think of your therapy bot as a **restaurant**:

### The Kitchen (Core Operations)
| File | Restaurant Role | What It Does |
|------|----------------|--------------|
| `main.py` | **Head Chef** | Coordinates everything, takes orders (messages) |
| `database.py` | **Recipe Book** | Remembers everything (users, messages, events) |
| `config.py` | **Restaurant Settings** | Hours, phone number, credentials |

### The Staff (Specialists)
| File | Restaurant Role | What It Does |
|------|----------------|--------------|
| `routers.py` | **Hostess** | Seats you with right therapist |
| `cbt_expert.py` | **Anxiety Chef** | Handles anxiety/depression |
| `mindfulness_expert.py` | **Zen Chef** | Handles stress/sleep |
| `motivation_expert.py` | **Energy Chef** | Handles ADHD/procrastination |

### The Helpers
| File | Restaurant Role | What It Does |
|------|----------------|--------------|
| `sms_handler.py` | **Delivery Driver** | Sends texts via Twilio |
| `event_extraction.py` | **Note Taker** | Writes down "test Friday" |
| `personalization.py` | **Style Expert** | Learns how you talk |
| `scheduler.py` | **Calendar** | Remembers to text you Thursday |
| `safety.py` | **Security** | Detects crisis, provides 988 |

---

## 💾 Database Tables

Your SQLite database (`data/users.db`) has these tables:

### 1. `users`
```
| id | user_id       | message_count | communication_style        |
|----|---------------|---------------|----------------------------|
| 1  | +19804060024  | 15            | {"formality": "casual"...} |
```

### 2. `messages`
```
| id | user_id | role      | content                      | timestamp           |
|----|---------|-----------|------------------------------|---------------------|
| 1  | 1       | user      | I have a test on Friday      | 2025-11-10 18:30:00 |
| 2  | 1       | assistant | I hear you're stressed...    | 2025-11-10 18:30:02 |
```

### 3. `important_events`
```
| id | user_id | type | description | event_date | completed |
|----|---------|------|-------------|------------|-----------|
| 1  | 1       | test | test        | 2025-11-14 | false     |
```

### 4. `scheduled_messages`
```
| id | user_id | message_content          | scheduled_time      | sent  |
|----|---------|--------------------------|---------------------|-------|
| 1  | 1       | Test is tomorrow...      | 2025-11-13 09:00:00 | false |
| 2  | 1       | How did test go?         | 2025-11-15 09:00:00 | false |
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────┐
│  YOUR PHONE │
└──────┬──────┘
       │ 1. Send SMS: "I have a test Friday"
       ▼
┌─────────────┐
│   TWILIO    │ (Receives SMS)
└──────┬──────┘
       │ 2. HTTP POST to /sms/webhook
       ▼
┌─────────────────────────────────────────────────┐
│           YOUR SERVER (main.py)                 │
│                                                  │
│  3. safety.py ──→ Crisis? ──→ No ✓              │
│           │                                      │
│           ▼                                      │
│  4. event_extraction.py ──→ Found "test Friday" │
│           │                  Save to database ✓  │
│           ▼                                      │
│  5. routers.py ──→ Route to CBT expert          │
│           │                                      │
│           ▼                                      │
│  6. cbt_expert.py ──→ Generate response          │
│           │                                      │
│           ▼                                      │
│  7. personalization.py ──→ Adapt to your style   │
│           │                                      │
│           ▼                                      │
│  8. Add event note ──→ "I've made a note..."     │
└──────────┬──────────────────────────────────────┘
           │ 9. sms_handler.py sends SMS
           ▼
┌─────────────┐
│   TWILIO    │ (Sends SMS back)
└──────┬──────┘
       │ 10. SMS delivered
       ▼
┌─────────────┐
│  YOUR PHONE │ Receives: "I hear you're stressed..."
└─────────────┘

Meanwhile, in the background:

┌─────────────────────────────────┐
│  SCHEDULER (runs every minute)  │
│                                  │
│  Checks database every minute:  │
│  - Any messages due?             │
│  - Thursday 9 AM? Send reminder  │
│  - Saturday 9 AM? Send follow-up │
└─────────────────────────────────┘
```

---

## 🎓 Key Concepts

### 1. Webhooks
**What:** Twilio calls your server when you send SMS
**Why:** Real-time communication
**How:** HTTP POST to `/sms/webhook`

### 2. Background Scheduler
**What:** Runs every minute checking for messages to send
**Why:** Proactive follow-ups (doesn't wait for you)
**How:** APScheduler library

### 3. Event Extraction
**What:** Finds events in your messages
**Why:** Enables proactive support
**How:** Regex patterns + date parsing

### 4. Personalization
**What:** Learns your texting style
**Why:** Feels more natural/human
**How:** Analyzes past 50 messages

### 5. MoE Routing
**What:** Picks which expert to use
**Why:** Different problems need different approaches
**How:** AI embeddings (sentence transformers)

---

## 🚀 Next Steps to Get Working

1. **Finish dependencies** (installing now...)
2. **Add Twilio credentials** to `.env`
3. **Start server**: `python python_ai/main.py`
4. **Start ngrok**: `ngrok http 8000`
5. **Configure Twilio webhook**
6. **Text your bot!**

Full guide: See `QUICK_START.md`
