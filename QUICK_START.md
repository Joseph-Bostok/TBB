# Quick Start Guide - Get SMS Working in 15 Minutes

## Prerequisites
- Twilio account with phone number
- Python 3.8+ installed
- Your phone number to test with

## Step 1: Install Dependencies (2 minutes)

```bash
cd /home/user/TBB

# Create virtual environment if not exists
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install everything
pip install -r python_ai/requirements.txt
```

This installs:
- FastAPI (web server)
- Twilio (SMS sending)
- SQLAlchemy (database)
- APScheduler (background tasks)
- sentence-transformers (AI routing)

## Step 2: Configure Twilio Credentials (3 minutes)

Edit `.env` file and add your credentials:

```bash
# Open .env in your editor
nano .env  # or use: code .env
```

Update these lines:
```bash
# Replace with YOUR credentials from Twilio console
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio number
```

**Where to find:**
1. Account SID: https://console.twilio.com (starts with "AC")
2. Auth Token: https://console.twilio.com → Copy the Auth Token
3. Phone Number: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

## Step 3: Test Server Locally (2 minutes)

```bash
# Start the server
python python_ai/main.py
```

You should see:
```
INFO: Initializing database...
INFO: Database tables created successfully
INFO: SMS enabled with Twilio number: +1234567890
INFO: Therapy Bot ready on http://0.0.0.0:8000
```

**If you see errors:**
- Missing dependencies? Run: `pip install -r python_ai/requirements.txt`
- Auth token missing? Update `.env` file

## Step 4: Test Without SMS First (1 minute)

Open a new terminal and test the API:

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"user": "test_user", "message": "I have a test on Friday"}'
```

Should return JSON with bot's response.

## Step 5: Install ngrok (2 minutes)

ngrok exposes your localhost to the internet so Twilio can reach it.

```bash
# macOS
brew install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Or download: https://ngrok.com/download
```

## Step 6: Start ngrok (1 minute)

In a NEW terminal window:

```bash
ngrok http 8000
```

You'll see:
```
Forwarding   https://abc123def456.ngrok.io -> http://localhost:8000
```

**Copy that HTTPS URL!** (e.g., `https://abc123def456.ngrok.io`)

**IMPORTANT:** Keep this terminal window open!

## Step 7: Configure Twilio Webhook (3 minutes)

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number
3. Scroll to "Messaging Configuration"
4. Under "A MESSAGE COMES IN":
   - Set to: **Webhook**
   - URL: `https://abc123def456.ngrok.io/sms/webhook`
     (Replace with YOUR ngrok URL + `/sms/webhook`)
   - HTTP Method: **POST**
5. Click **Save**

## Step 8: Send Your First Text! (1 minute)

From your phone, text your Twilio number:

```
Hi, I'm testing this bot
```

**You should get a response!**

## Step 9: Test Event Tracking

Text:
```
I have a test on Friday and I'm stressed about it
```

Bot should:
1. Respond with anxiety support
2. Say "I've made a note about your test on Friday"
3. (Will send follow-up on Thursday/Saturday)

## Troubleshooting

### No response received?

**Check server logs:**
```bash
# In the terminal running main.py
# Look for: "Received SMS from +1..."
```

**Check ngrok:**
Go to: http://localhost:4040
- See requests from Twilio?
- Any errors?

**Check Twilio:**
Go to: https://console.twilio.com/us1/monitor/logs/debugger
- See your message?
- Any errors?

### "SMS not configured" in logs?

Check `.env` file:
```bash
cat .env | grep TWILIO
```

Make sure all three are set:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER

### ngrok URL changed?

ngrok gives you a new URL each time you restart it (unless you have a paid account).

**When it changes:**
1. Copy new URL
2. Update Twilio webhook
3. Restart your test

### Server crashes?

Check logs:
```bash
tail -f logs/therapy_bot.log
```

Common issues:
- Missing Auth Token → Update `.env`
- Port 8000 in use → Change PORT in `.env`
- Dependencies missing → Run `pip install -r python_ai/requirements.txt`

## What's Happening Behind the Scenes

When you text "I have a test Friday":

1. **Twilio** receives your SMS
2. **Sends HTTP POST** to your ngrok URL
3. **ngrok tunnels** to localhost:8000
4. **main.py /sms/webhook** receives it
5. **event_extraction.py** finds "test" + "Friday"
6. **Saves event** to database
7. **routers.py** routes to CBT expert
8. **cbt_expert.py** generates response
9. **personalization.py** adapts to your style
10. **sms_handler.py** sends via Twilio
11. **You receive** the response!
12. **scheduler.py** creates follow-ups for Thursday/Saturday

## Next Steps

### Test More Features

**Crisis Detection:**
```
I'm feeling really hopeless
```
Should get 988 hotline info.

**Different Experts:**
```
I can't sleep and feel stressed
```
Routes to Mindfulness expert.

```
I keep procrastinating on my work
```
Routes to Motivation expert.

**Multiple Events:**
```
I have a presentation on Monday and a doctor appointment on Wednesday
```
Tracks both events.

### View Your Data

Check the database:
```bash
sqlite3 data/users.db

-- See your messages
SELECT * FROM messages;

-- See tracked events
SELECT * FROM important_events;

-- See scheduled follow-ups
SELECT * FROM scheduled_messages;

-- Exit
.quit
```

### Monitor Logs

Watch in real-time:
```bash
tail -f logs/therapy_bot.log
```

## Production Deployment (Later)

For real use (not localhost):

1. Deploy to: Heroku, Railway, DigitalOcean, AWS
2. Get permanent domain/URL
3. Update Twilio webhook to production URL
4. No need for ngrok!
5. Add HTTPS certificate
6. Set up monitoring

## Important Notes

⚠️ **This is a demo** - Not HIPAA compliant
⚠️ **Keep .env secure** - Never commit to GitHub
⚠️ **Free trial limits** - Can only text verified numbers
⚠️ **ngrok restarts** - URL changes each time

## Need Help?

Check the full guide: `SMS_SETUP_GUIDE.md`

Or check logs:
```bash
# Server logs
tail -f logs/therapy_bot.log

# ngrok requests
http://localhost:4040
```
