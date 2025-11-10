# Claude AI Integration Guide

Your therapy bot now supports **Claude AI** for truly conversational, empathetic responses!

## Why Claude?

- **Empathetic:** Excellent at emotional intelligence and therapy
- **Conversational:** Natural, human-like responses
- **Context-aware:** Remembers your conversation history
- **ADHD-friendly:** Great at breaking down tasks and providing structure
- **Long memory:** Can handle extensive conversation context

---

## Step 1: Get Your Claude API Key

### Create Anthropic Account

1. Go to: **https://console.anthropic.com**
2. Sign up for an account (or log in)
3. Click **"Get API Keys"** or **"API Keys"** in the sidebar

### Get API Key

1. Click **"Create Key"**
2. Name it: `Therapy Bot`
3. Copy the API key (starts with `sk-ant-`)
4. **Save it somewhere safe!** You won't see it again

### Add Credits

**Important:** Claude API requires credits to use.

- New accounts get **$5 free credits**
- Add more at: https://console.anthropic.com/settings/billing
- Costs about **$0.003 per conversation** (very cheap!)

---

## Step 2: Configure Your Bot

Edit your `.env` file:

```bash
# Open .env
nano .env  # or: code .env
```

Update these lines:

```bash
# Set to false to enable Claude
USE_MOCK_MODELS=false

# Add your API key
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Example:**
```bash
USE_MOCK_MODELS=false
ANTHROPIC_API_KEY=sk-ant-api03-ABC123xyz...
```

Save and close.

---

## Step 3: Install Anthropic Library

```bash
# Activate virtual environment
source venv/bin/activate

# Install Claude library
./venv/bin/pip install anthropic==0.40.0
```

---

## Step 4: Test It!

### Option A: Test Locally (No SMS)

```bash
python test_bot.py
```

You'll see Claude generate the response instead of rule-based responses!

### Option B: Test via API

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "test", "message": "I have a test tomorrow and I am really stressed"}'
```

Look for in the response - it will be much more conversational!

### Option C: Text Your Bot (SMS)

Once you have SMS set up (see `QUICK_START.md`), just text your number and you'll get Claude-powered responses!

---

## How It Works

```
You: "I have a test tomorrow and I'm really stressed"

WITHOUT Claude (rule-based):
Bot: "Test anxiety is common. Try these CBT techniques..."
(Generic, template-like)

WITH Claude:
Bot: "Hey, I can hear how stressed you're feeling about tomorrow's test.
That pressure is really real, especially when you're already worried about it.
Let's break this down together - what subject is it, and how's your prep been going so far?"
(Natural, empathetic, conversational)
```

Claude:
- Asks follow-up questions
- Validates your emotions
- Adapts to your communication style
- Remembers previous conversations
- Provides personalized advice

---

## Checking If It's Working

### Look at Server Logs

When you start the server:

```bash
python python_ai/main.py
```

You should see:
```
INFO: Claude expert initialized with API key
```

When processing messages:
```
INFO: Using Claude AI for cbt response
```

### Check Response Quality

Claude responses will:
- Be more conversational and natural
- Ask thoughtful follow-up questions
- Reference previous conversations
- Adapt tone to match yours
- Feel like texting a real person

---

## Cost Estimation

Claude is **very affordable**:

| Usage | Cost |
|-------|------|
| 1 message | ~$0.003 (less than a penny) |
| 100 messages | ~$0.30 |
| 1000 messages | ~$3.00 |
| Monthly (30 msgs/day) | ~$2.70 |

**Free $5 credits = ~1,666 messages!**

---

## Switching Between Modes

### Use Claude (Conversational AI)
```bash
# In .env
USE_MOCK_MODELS=false
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Use Rule-Based (Free, No API)
```bash
# In .env
USE_MOCK_MODELS=true
# ANTHROPIC_API_KEY not needed
```

The bot automatically falls back to rule-based if:
- No API key provided
- API key invalid
- API error occurs

---

## Example Conversation with Claude

```
You: hey, i keep procrastinating on my homework

Bot: I get it - procrastination is such a common struggle, especially with ADHD.
     It's frustrating when you know you need to do something but just can't get started, right?

     What's the homework you're putting off? Let's see if we can make it feel less overwhelming.

You: math problems. i have like 20 to do

Bot: Okay, 20 problems can definitely feel like a lot when you're looking at the whole thing.

     Here's a quick trick that helps a lot of people: pick just ONE problem to do right now.
     Not all 20, not even 5 - just one. Can you do that? Sometimes getting that first one done
     breaks the mental block.

You: ok i did one

Bot: Yes! That's actually huge. You just proved to yourself you CAN do it.

     How does it feel? And honestly - do you feel like you could maybe do one or two more
     now that you've started, or do you need a break?
```

Notice how Claude:
- ✅ Uses natural language ("I get it")
- ✅ Validates feelings
- ✅ Breaks tasks down (ADHD-friendly)
- ✅ Asks follow-up questions
- ✅ Celebrates small wins
- ✅ Feels like a real conversation

---

## Troubleshooting

### "Claude expert initialized without API key"

**Problem:** No API key in `.env`
**Solution:** Add `ANTHROPIC_API_KEY=sk-ant-...` to `.env`

### "Using rule-based expert" (but you want Claude)

**Problem:** `USE_MOCK_MODELS=true` in `.env`
**Solution:** Change to `USE_MOCK_MODELS=false`

### "Claude API error: authentication failed"

**Problem:** Invalid API key
**Solution:**
1. Go to https://console.anthropic.com
2. Generate new API key
3. Update `.env` with new key

### "Claude API error: insufficient credits"

**Problem:** Out of credits
**Solution:**
1. Go to https://console.anthropic.com/settings/billing
2. Add payment method
3. Add credits ($10-20 lasts a long time)

### Responses still feel generic

**Problem:** Claude needs more context
**Solution:** Have a longer conversation - Claude gets better as it learns your style

---

## Next Steps

1. **Get API key** from https://console.anthropic.com
2. **Add to `.env`** file
3. **Set `USE_MOCK_MODELS=false`**
4. **Install anthropic**: `pip install anthropic`
5. **Test it!** Text your bot or run `python test_bot.py`

Your therapy bot will now have truly conversational, empathetic responses powered by Claude AI! 🚀

---

## Resources

- Anthropic Console: https://console.anthropic.com
- Claude API Docs: https://docs.anthropic.com
- Pricing: https://www.anthropic.com/pricing
- Status: https://status.anthropic.com
