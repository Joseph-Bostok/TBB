# Twilio SMS Bot - Setup Checklist

Use this checklist to get your SMS therapy bot running.

## ☑️ Pre-Setup (Already Done!)

- [x] Twilio account created
- [x] Twilio credentials configured in `.env`
- [x] Phone number acquired: `+18553592165`
- [x] Code is ready to go!

## 📋 Setup Steps

### 1. Complete Twilio Verification

**Status:** ⏳ Waiting for Twilio approval

**What to do:**
1. Go to https://console.twilio.com
2. Complete the verification process Twilio is requesting
3. This is required to send SMS to non-verified numbers

**Once approved:** ✅ Mark this complete

---

### 2. Install ngrok (For Local Testing)

**What is ngrok?**
Creates a public URL that forwards to your local server (localhost:8000).
Twilio needs this to send incoming messages to your computer.

**Install:**
```bash
# Option 1: Download from website
# Go to: https://ngrok.com/download

# Option 2: Package manager
brew install ngrok  # macOS
# OR
sudo snap install ngrok  # Linux
```

**Test it works:**
```bash
ngrok http 8000
# You should see: Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

Press `Ctrl+C` to stop (we'll start it properly later).

**Once installed:** ✅ Mark this complete

---

### 3. Start Everything

**One command to rule them all:**

```bash
cd ~/TTB
./START_SMS_BOT.sh
```

This will:
- ✓ Create virtual environment (if needed)
- ✓ Install dependencies
- ✓ Start the server
- ✓ Give you next steps

**In a separate terminal, start ngrok:**
```bash
ngrok http 8000
```

Copy the `https://` URL (e.g., `https://abc123.ngrok.io`)

---

### 4. Configure Twilio Webhook

**Tell Twilio where to send incoming SMS:**

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your number: `+18553592165`
3. Scroll to "Messaging Configuration"
4. Under "A MESSAGE COMES IN":
   - **Webhook:** `https://YOUR-NGROK-URL.ngrok.io/sms/webhook`
   - Example: `https://abc123.ngrok.io/sms/webhook`
   - **Method:** HTTP POST
5. Click **Save Configuration**

**Once configured:** ✅ Mark this complete

---

### 5. Test Your Bot! 🎉

**Send an SMS to:** `+18553592165`

**Try these messages:**
- "I'm feeling anxious"
- "I need help with stress"
- "What is CBT?"
- "I'm having a bad day"

**You should receive an AI response within seconds!**

---

## 🔍 Verify Everything Works

Run the automated test:

```bash
cd ~/TTB
python test_twilio_setup.py
```

This checks:
- ✓ `.env` configuration
- ✓ Twilio credentials
- ✓ Server is running
- ✓ ngrok is running
- ✓ Webhook endpoint works

---

## 📱 Using Your Bot

Once setup is complete:

1. **Anyone can text** `+18553592165`
2. **The bot remembers** conversations (by phone number)
3. **AI responds** with therapy techniques
4. **Crisis detection** is active for safety

---

## 🛠 Common Issues

### "Message not delivered"
**Fix:** Check ngrok URL matches Twilio webhook exactly
```bash
# Get current ngrok URL:
curl http://localhost:4040/api/tunnels | grep public_url
```

### "Server not responding"
**Fix:** Restart the server
```bash
cd ~/TTB/python_ai
python main.py
```

### "ngrok URL changed"
**Why:** Free ngrok gives you a new URL each restart
**Fix:** Update Twilio webhook with new URL

**Pro tip:** Get a static ngrok domain ($8/mo) to avoid this

---

## 🚀 Production Deployment (Later)

When ready to deploy to a real server:

1. Deploy to AWS/Heroku/DigitalOcean
2. Get a domain with HTTPS
3. Update Twilio webhook to: `https://yourdomain.com/sms/webhook`
4. No ngrok needed!

---

## ✅ Final Checklist

Before testing:

- [ ] Twilio verification complete
- [ ] ngrok installed and running
- [ ] Server running (port 8000)
- [ ] Twilio webhook configured with ngrok URL
- [ ] Test message sent
- [ ] Bot responded!

---

## 🎯 Quick Reference

| What | Where |
|------|-------|
| **Start bot** | `./START_SMS_BOT.sh` |
| **Start ngrok** | `ngrok http 8000` |
| **Test setup** | `python test_twilio_setup.py` |
| **View logs** | `tail -f python_ai/logs/therapy_bot.log` |
| **Phone number** | `+18553592165` |
| **Twilio Console** | https://console.twilio.com |
| **ngrok Dashboard** | http://localhost:4040 |

---

**You're all set! Text the bot to start chatting! 📱**
