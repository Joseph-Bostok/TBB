# SMS Therapy Bot Setup Guide

This guide will help you set up the Therapy Bot to receive and send text messages via Twilio.

## Table of Contents
1. [Twilio Account Setup](#twilio-account-setup)
2. [Get a Phone Number](#get-a-phone-number)
3. [Configure Environment Variables](#configure-environment-variables)
4. [Expose Your Server (ngrok)](#expose-your-server-ngrok)
5. [Configure Twilio Webhook](#configure-twilio-webhook)
6. [Test the Integration](#test-the-integration)
7. [Troubleshooting](#troubleshooting)

---

## Twilio Account Setup

### 1. Create a Twilio Account
1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free trial account
3. Verify your email and phone number

### 2. Get Your Credentials
1. Once logged in, go to the [Twilio Console](https://console.twilio.com)
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Copy these - you'll need them for the `.env` file

**Free Trial Limits:**
- $15.50 credit
- Can only send to verified phone numbers
- Messages include "Sent from a Twilio trial account"

---

## Get a Phone Number

### 1. Purchase/Get a Twilio Number
1. In the Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select your country (usually United States)
3. Check **SMS** capability
4. Click **Search**
5. Choose a number you like
6. Click **Buy** (free with trial account)

### 2. Note Your Number
- Copy the phone number (format: +15551234567)
- You'll need this for the `.env` file

---

## Configure Environment Variables

### 1. Create .env File
```bash
cd /path/to/TBB
cp .env.example .env
```

### 2. Edit .env File
Open `.env` and add your Twilio credentials:

```bash
# SMS Integration (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# For now, use localhost (we'll change this next)
WEBHOOK_BASE_URL=http://localhost:8000
```

---

## Expose Your Server (ngrok)

For local development, you need to expose your localhost to the internet so Twilio can send webhooks to your server.

### 1. Install ngrok
```bash
# macOS
brew install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Or download from https://ngrok.com/download
```

### 2. Start ngrok
In a **separate terminal**, run:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123def456.ngrok.io -> http://localhost:8000
```

### 3. Update .env
Copy the HTTPS URL from ngrok and update your `.env`:

```bash
WEBHOOK_BASE_URL=https://abc123def456.ngrok.io
```

**Important:** Keep ngrok running while testing!

---

## Configure Twilio Webhook

### 1. Set Up Messaging Webhook
1. Go to [Twilio Console](https://console.twilio.com) → **Phone Numbers** → **Manage** → **Active Numbers**
2. Click on your phone number
3. Scroll down to **Messaging Configuration**
4. Under **A MESSAGE COMES IN**:
   - Set to: **Webhook**
   - URL: `https://abc123def456.ngrok.io/sms/webhook` (replace with your ngrok URL)
   - HTTP Method: **POST**
5. Click **Save**

### 2. Verify Configuration
Your webhook URL should look like:
```
https://abc123def456.ngrok.io/sms/webhook
```

---

## Test the Integration

### 1. Start the Server
```bash
# Activate virtual environment
source venv/bin/activate

# Start the therapy bot server
python python_ai/main.py
```

You should see:
```
INFO: SMS enabled with Twilio number: +15551234567
INFO: Therapy Bot ready on http://0.0.0.0:8000
```

### 2. Send a Test Message
**From your phone**, send a text message to your Twilio number:

```
Hi, I'm feeling anxious today
```

### 3. Check for Response
You should receive a response from the bot within seconds!

### 4. Test Event Extraction
Try mentioning an event:

```
I have a test on Friday and I'm really stressed about it
```

The bot should:
1. Acknowledge your stress
2. Tell you it's made a note about your test
3. Send follow-up messages leading up to Friday

---

## How It Works

### Message Flow
```
[User Phone]
    ↓ SMS
[Twilio]
    ↓ HTTP POST /sms/webhook
[Your Server]
    → Process message
    → Detect crisis/events
    → Route to expert
    → Apply personalization
    ↓
[Twilio API]
    ↓ SMS
[User Phone receives response]
```

### Proactive Follow-Ups
```
User: "I have a test on Friday"
    ↓
Bot creates scheduled messages:
    - Thursday 9 AM: "Your test is tomorrow. How's prep going?"
    - Saturday 9 AM: "How did your test go?"
```

### Personalization
The bot learns your style over time:
- Message length preferences
- Emoji usage
- Formality level (casual vs formal)
- Greeting style (Hi, Hey, Hello)

---

## Troubleshooting

### No Response Received

**Check ngrok:**
```bash
# Visit ngrok web interface
http://localhost:4040
```
- Check if Twilio is sending requests
- Look for errors in the request logs

**Check server logs:**
```bash
tail -f logs/therapy_bot.log
```
- Look for "Received SMS from..."
- Check for errors

**Verify webhook URL:**
- Go to Twilio Console → Phone Numbers
- Make sure webhook URL is correct
- Must use HTTPS (not HTTP)

### "Sent from a Twilio trial account"

This is normal for trial accounts. To remove:
1. Upgrade to a paid account
2. Add billing information

### Message Not Sending

**Check .env credentials:**
```bash
cat .env | grep TWILIO
```

**Test SMS sending manually:**
```bash
# In Python shell
from python_ai.sms_handler import get_sms_handler

sms = get_sms_handler()
print(sms.is_enabled())  # Should be True

success, result = await sms.send_sms("+15551234567", "Test")
print(success, result)
```

### Rate Limit Exceeded

Trial accounts have limits:
- 1 message per second
- Limited total messages

**Solution:** Wait or upgrade account

---

## Production Deployment

For production deployment (not localhost):

### 1. Deploy to a Server
Options:
- **Heroku** (easiest)
- **Railway**
- **DigitalOcean**
- **AWS**

### 2. Update Webhook URL
1. Set `WEBHOOK_BASE_URL` to your production URL
2. Update Twilio webhook to production URL
3. No need for ngrok!

### 3. Security Considerations
- [ ] Enable HTTPS (required by Twilio)
- [ ] Validate Twilio signatures (prevent spoofing)
- [ ] Set up proper logging and monitoring
- [ ] Configure rate limiting
- [ ] Set up crisis alert emails

### 4. HIPAA Compliance
**IMPORTANT:** This demo is NOT HIPAA compliant.

For production mental health apps:
- [ ] Use Twilio's HIPAA-eligible products
- [ ] Sign BAA (Business Associate Agreement) with Twilio
- [ ] Encrypt database at rest
- [ ] Set up audit logging
- [ ] Get legal/compliance review
- [ ] Have licensed clinician oversight

---

## Next Steps

### Try These Features:

1. **Event Tracking:**
   - "I have a presentation next Tuesday"
   - "My therapy appointment is on Thursday"

2. **Personalization:**
   - Send 10+ messages in your style
   - Watch the bot adapt to your communication

3. **Crisis Detection:**
   - Mention feeling hopeless (bot provides resources)

4. **Different Experts:**
   - Anxiety/depression → CBT expert
   - Stress/sleep → Mindfulness expert
   - Procrastination → Motivation expert

---

## Resources

- [Twilio SMS Documentation](https://www.twilio.com/docs/sms)
- [Twilio Python Quickstart](https://www.twilio.com/docs/sms/quickstart/python)
- [ngrok Documentation](https://ngrok.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## Support

If you encounter issues:
1. Check the logs: `tail -f logs/therapy_bot.log`
2. Check ngrok dashboard: `http://localhost:4040`
3. Review Twilio debugger: [Console → Monitor → Logs](https://console.twilio.com/monitor/logs/debugger)

**Remember:** This is a demo for learning. For production mental health applications, consult with licensed clinicians and ensure HIPAA compliance.
