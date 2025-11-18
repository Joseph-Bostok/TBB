# Firebase Phone Authentication Setup Guide

This guide explains how to use Firebase Phone Authentication with the TBB Therapy Bot instead of Twilio.

## Why Firebase Phone Authentication?

- **Easier Setup**: No business verification required for testing
- **Built-in Verification**: Firebase handles SMS sending and code verification
- **Free Tier**: Generous free quota for development and testing
- **Global Coverage**: Works in most countries worldwide

## Architecture Overview

```
┌─────────────────┐
│  User's Phone   │
│   (Client)      │
└────────┬────────┘
         │ 1. Enter phone number
         ▼
┌─────────────────┐
│  Firebase SDK   │  (Client-side JavaScript/Mobile)
│  (Web/Mobile)   │
└────────┬────────┘
         │ 2. Send verification code via SMS
         │ 3. User enters code
         │ 4. Get ID Token
         ▼
┌─────────────────┐
│  Backend API    │  POST /auth/verify-phone
│  (Python)       │
└────────┬────────┘
         │ 5. Verify token with Firebase Admin SDK
         │ 6. Create/get user in database
         ▼
┌─────────────────┐
│  SQLite DB      │  Store user with phone number
└─────────────────┘
```

## Backend Setup (Already Complete!)

The backend is already configured with:

✅ Firebase Admin SDK installed (`firebase-admin==6.3.0`)
✅ Firebase credentials configured in `.env`
✅ Phone verification endpoint at `POST /auth/verify-phone`
✅ Firebase authentication module (`firebase_auth.py`)

### Backend Endpoint

**POST /auth/verify-phone**

Request:
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "success": true,
  "phone_number": "+15551234567",
  "user_id": "+15551234567",
  "message": "Phone number verified successfully"
}
```

## Frontend/Client Setup

You need to implement a client-side interface (web or mobile app) that uses Firebase to collect and verify phone numbers.

### Option 1: Web Client (HTML + JavaScript)

Create a simple HTML page with Firebase JavaScript SDK:

#### 1. Create HTML File

Create `test-firebase-auth.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>TBB Phone Verification</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            font-size: 16px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        #status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        #recaptcha-container {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>TBB Phone Verification</h1>

    <div id="phone-input-section">
        <input type="tel" id="phone-number" placeholder="+1 555 123 4567" />
        <div id="recaptcha-container"></div>
        <button id="send-code-button" onclick="sendVerificationCode()">Send Verification Code</button>
    </div>

    <div id="code-input-section" style="display:none;">
        <input type="text" id="verification-code" placeholder="Enter 6-digit code" maxlength="6" />
        <button onclick="verifyCode()">Verify Code</button>
    </div>

    <div id="status"></div>

    <!-- Firebase JavaScript SDK -->
    <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>

    <script>
        // Firebase configuration
        // Replace with your Firebase project config
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "tbb-therapy-app.firebaseapp.com",
            projectId: "tbb-therapy-app",
            storageBucket: "tbb-therapy-app.appspot.com",
            messagingSenderId: "YOUR_SENDER_ID",
            appId: "YOUR_APP_ID"
        };

        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();

        // Setup reCAPTCHA verifier
        window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
            'size': 'normal',
            'callback': (response) => {
                // reCAPTCHA solved
                console.log('reCAPTCHA solved');
            }
        });

        let confirmationResult;

        // Send verification code
        async function sendVerificationCode() {
            const phoneNumber = document.getElementById('phone-number').value;
            const appVerifier = window.recaptchaVerifier;
            const button = document.getElementById('send-code-button');

            button.disabled = true;
            showStatus('Sending verification code...', false);

            try {
                confirmationResult = await auth.signInWithPhoneNumber(phoneNumber, appVerifier);
                showStatus('Verification code sent! Check your phone.', true);
                document.getElementById('phone-input-section').style.display = 'none';
                document.getElementById('code-input-section').style.display = 'block';
            } catch (error) {
                console.error('Error sending code:', error);
                showStatus('Error: ' + error.message, false);
                button.disabled = false;
                grecaptcha.reset(window.recaptchaWidgetId);
            }
        }

        // Verify the code
        async function verifyCode() {
            const code = document.getElementById('verification-code').value;
            showStatus('Verifying code...', false);

            try {
                // Verify the SMS code
                const result = await confirmationResult.confirm(code);
                const user = result.user;

                // Get the ID token
                const idToken = await user.getIdToken();

                showStatus('Code verified! Authenticating with backend...', true);

                // Send token to backend
                const response = await fetch('http://localhost:8000/auth/verify-phone', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ id_token: idToken })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus(`Success! Authenticated as ${data.phone_number}`, true);
                    console.log('User data:', data);
                } else {
                    showStatus('Backend authentication failed: ' + data.message, false);
                }

            } catch (error) {
                console.error('Error verifying code:', error);
                showStatus('Error: ' + error.message, false);
            }
        }

        function showStatus(message, isSuccess) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = isSuccess ? 'success' : 'error';
        }
    </script>
</body>
</html>
```

#### 2. Get Firebase Web Configuration

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project ("tbb-therapy-app")
3. Click the **gear icon** → **Project settings**
4. Scroll down to **"Your apps"** section
5. Click the **Web icon** (`</>`) to add a web app
6. Register app with nickname (e.g., "TBB Web Client")
7. Copy the `firebaseConfig` object
8. Replace the `firebaseConfig` in the HTML file above

#### 3. Test Locally

```bash
# Serve the HTML file (use any simple HTTP server)
python3 -m http.server 8080

# Then open in browser:
# http://localhost:8080/test-firebase-auth.html
```

### Option 2: Mobile App (React Native, Flutter, etc.)

Use Firebase Authentication SDK for your mobile platform:
- **React Native**: `@react-native-firebase/auth`
- **Flutter**: `firebase_auth` package
- **iOS Native**: FirebaseAuth pod
- **Android Native**: firebase-auth dependency

The flow is the same:
1. Collect phone number
2. Send verification code
3. Verify code
4. Get ID token
5. Send to backend `/auth/verify-phone`

## Testing Phone Verification

### Test Phone Numbers (Development Only)

Firebase allows you to configure test phone numbers that don't send real SMS:

1. Go to Firebase Console → **Authentication** → **Sign-in method**
2. Click **Phone** provider
3. Expand **"Phone numbers for testing"**
4. Add test numbers with verification codes:
   - Phone: `+1 555 123 4567`
   - Code: `123456`

### Testing Flow

1. **Start the backend**:
   ```bash
   cd /home/user/TBB/python_ai
   python main.py
   ```

2. **Open the web client** (or mobile app)

3. **Enter phone number**: `+1 555 123 4567`

4. **Click "Send Verification Code"** (reCAPTCHA will appear)

5. **Enter the code**: `123456` (or the code you received via SMS)

6. **Verify**: The backend will verify the token and create the user

7. **Check logs**:
   ```bash
   tail -f logs/therapy_bot.log
   ```

   You should see:
   ```
   INFO - Phone verification successful for +15551234567
   ```

## Production Deployment

### Before Going to Production:

1. **Remove test phone numbers** from Firebase Console

2. **Configure SMS quota**:
   - Firebase free tier: 10k verifications/month
   - Upgrade to Blaze plan for more

3. **Add App Verification**:
   - **Web**: reCAPTCHA is required (already in example)
   - **iOS**: Automatic app verification
   - **Android**: SHA-256 fingerprint required

4. **Enable phone authentication regions**:
   - Go to Firebase Console → Authentication → Settings
   - Configure allowed countries

5. **Monitor usage**:
   - Firebase Console → Authentication → Usage tab

## Security Considerations

- ✅ **ID tokens expire**: Tokens are valid for 1 hour
- ✅ **HTTPS required**: Use HTTPS in production
- ✅ **Rate limiting**: Firebase has built-in rate limiting
- ✅ **Credentials secured**: Service account key is gitignored
- ⚠️ **Never commit** `firebase-credentials.json` to version control

## Troubleshooting

### "Firebase not initialized"
- Check that `firebase-credentials.json` exists in project root
- Verify `FIREBASE_CREDENTIALS_PATH` in `.env` is correct

### "Invalid ID token"
- Token may be expired (they last 1 hour)
- Client may not be using the correct Firebase project
- Check that client's `firebaseConfig` matches your project

### "Phone number not in E.164 format"
- Ensure phone numbers include country code: `+1...`
- Use international format: `+[country][area][number]`

### "reCAPTCHA error"
- Make sure you're serving HTML over HTTP/HTTPS (not file://)
- Check Firebase Console → Authentication → Sign-in method → Phone is enabled
- For localhost testing, Firebase should auto-approve reCAPTCHA

## Next Steps

1. ✅ **Backend is ready** - Phone auth endpoint is live
2. 📱 **Create frontend** - Build web or mobile client
3. 🧪 **Test with test numbers** - Use Firebase test phone numbers
4. 🚀 **Deploy to production** - Remove test numbers and deploy

## Support

For issues:
- Firebase docs: https://firebase.google.com/docs/auth/web/phone-auth
- Backend logs: `tail -f logs/therapy_bot.log`
- API docs: http://localhost:8000/docs (when server is running)
