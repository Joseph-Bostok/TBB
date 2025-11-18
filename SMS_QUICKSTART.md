# SMS Therapy Bot - Quick Start Guide

This guide will get your SMS therapy bot up and running in minutes once Twilio is authorized.

## ✅ What's Already Set Up

Your bot is **ready to go!** Here's what's already configured:

- ✅ Twilio credentials in `.env`
- ✅ SMS webhook endpoint: `POST /sms/webhook`
- ✅ AI therapy bot with conversation memory
- ✅ Crisis detection and safety features
- ✅ Phone number: `+18553592165`

## 🚀 Quick Start (3 Steps)

### Step 1: Complete Twilio Verification

Twilio is asking for verification to enable SMS sending. Complete this once:

1. Go to https://console.twilio.com
2. Complete the verification process they're requesting
   - This might include phone verification, business info, or A2P registration
   - **Required for production SMS sending**
3. Once approved, you can send SMS to any phone number

**During verification?** You can still test with verified numbers:
- Add test numbers at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified

---

### Step 2: Make Server Publicly Accessible

Twilio needs to reach your server. Use **ngrok** for testing:

#### Install ngrok (one-time):
```bash
# Download from https://ngrok.com/download
# Or install via package manager:
brew install ngrok  # macOS
# OR
sudo snap install ngrok  # Linux
```

#### Run ngrok:
```bash
# In a NEW terminal (keep your server running in another):
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the `https://abc123.ngrok.io` URL** - you'll need it in Step 3.

---

### Step 3: Configure Twilio Webhook

Tell Twilio where to send incoming SMS messages:

1. **Go to**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. **Click** your phone number: `+18553592165`
3. **Scroll to** "Messaging Configuration"
4. **Under "A MESSAGE COMES IN"**:
   - Webhook URL: `https://YOUR-NGROK-URL.ngrok.io/sms/webhook`
   - Example: `https://abc123.ngrok.io/sms/webhook`
   - Method: **HTTP POST** ✓
5. **Click "Save"**

**Important:** Update the webhook URL every time you restart ngrok (it changes each time on free plan).

---

## 🧪 Test Your Bot

Once setup is complete:

1. **Send an SMS** to `+18553592165` from your phone
2. **Type any message**, like:
   - "I'm feeling anxious"
   - "I need help with stress"
   - "Tell me about cognitive behavioral therapy"

3. **You'll receive an AI response** within seconds!

### What Happens Behind the Scenes:

```
Your Phone
    ↓ (SMS to +18553592165)
Twilio
    ↓ (POST to /sms/webhook)
Your Server (via ngrok)
    ↓ (AI processes message)
Claude AI / Therapy Experts
    ↓ (Response generated)
Twilio
    ↓ (SMS back to you)
Your Phone (receives AI reply)
```

---

## 🔍 Verify Everything is Working

Run this test script to check your setup:

```bash
cd ~/TTB
python test_twilio_setup.py
```

This will verify:
- ✓ Twilio credentials are valid
- ✓ Phone number is configured
- ✓ Server endpoint is accessible
- ✓ ngrok is running (if applicable)

---

## 📱 Features Your Bot Has

Once running, users can text your bot and it will:

1. **Remember conversations** - Tracks history by phone number
2. **Route to appropriate experts**:
   - CBT (Cognitive Behavioral Therapy)
   - Mindfulness techniques
   - Motivational support
3. **Crisis detection** - Identifies concerning messages (suicide, self-harm, etc.)
4. **Personalization** - Learns user's communication style
5. **Event tracking** - Remember important dates and follow up

---

## 🛠 Troubleshooting

### "Message not received"
- ✓ Check ngrok is running
- ✓ Verify webhook URL in Twilio Console matches ngrok URL
- ✓ Check server logs: `tail -f logs/therapy_bot.log`

### "Invalid credentials" error
- ✓ Verify Twilio Account SID and Auth Token in `.env`
- ✓ Check at: https://console.twilio.com/us1/account/keys-credentials/api-keys

### "Phone number not verified" error
- ✓ Complete Twilio verification process
- ✓ Or add recipient's number as verified for testing

### ngrok URL changed
- Every time you restart ngrok (free plan), you get a new URL
- Update Twilio webhook with new ngrok URL
- **Pro tip:** Get a static ngrok URL with paid plan ($8/mo)

---

## 🎯 Production Deployment (Optional)

For production (not localhost):

1. **Deploy to a server** (AWS, Heroku, DigitalOcean, etc.)
2. **Get a domain** with HTTPS
3. **Update Twilio webhook** to your domain:
   - `https://yourdomain.com/sms/webhook`
4. **Update `.env`**:
   ```
   WEBHOOK_BASE_URL=https://yourdomain.com
   ```

No need for ngrok in production!

---

## 📋 Quick Reference

| Item | Value |
|------|-------|
| **Twilio Phone Number** | `+18553592165` |
| **Webhook Endpoint** | `/sms/webhook` |
| **Server Port** | `8000` |
| **Twilio Console** | https://console.twilio.com |
| **ngrok Dashboard** | http://localhost:4040 (when running) |

---

## 🆘 Need Help?

1. **Check server logs**: `tail -f ~/TTB/logs/therapy_bot.log`
2. **Check ngrok requests**: http://localhost:4040 (shows all HTTP requests)
3. **Twilio debugger**: https://console.twilio.com/us1/monitor/logs/debugger
4. **Test endpoint manually**:
   ```bash
   curl -X POST http://localhost:8000/sms/webhook \
     -d "From=+15551234567" \
     -d "Body=Hello bot"
   ```

---

## ✨ You're All Set!

Your SMS therapy bot is ready. Just:
1. ✅ Complete Twilio verification
2. ✅ Run ngrok
3. ✅ Configure webhook
4. 📱 Start texting!

**Text `+18553592165` to try it out!**
