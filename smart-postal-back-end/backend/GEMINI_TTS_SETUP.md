# Gemini 2.5 Pro TTS Setup for Sinhala

## Overview

Gemini 2.5 Pro TTS provides **premium quality** Sinhala text-to-speech via the Google Cloud Text-to-Speech v1beta1 API. This is the best option for natural Sinhala pronunciation.

## Requirements

The Gemini TTS model requires:
1. **Google Cloud project** with both APIs enabled:
   - Cloud Text-to-Speech API
   - Vertex AI API
2. **Billing** enabled on your project
3. **API key** with the `aiplatform.endpoints.predict` permission

## Current Status

⚠️ Your current API key (`GOOGLE_CLOUD_TTS_API_KEY`) doesn't have Vertex AI permissions.

The system will automatically **fallback to Azure TTS** which also provides good quality Sinhala with the neural voice `si-LK-SameeraNeural`.

## Option A: Enable Gemini TTS (Best Quality)

### Step 1: Enable Vertex AI API
1. Go to: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com
2. Click "ENABLE"

### Step 2: Create Service Account (Recommended)
API keys can't easily get Vertex AI permissions. Use a service account instead:

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Name: `tts-gemini-service`
4. Grant roles:
   - **Cloud Text-to-Speech User** (`roles/texttospeech.user`)
   - **Vertex AI User** (`roles/aiplatform.user`)
5. Create JSON key and download

### Step 3: Configure Service Account
Save the JSON key to:
```
smart-postal-back-end/backend/config/service-account-gemini.json
```

Update `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=config/service-account-gemini.json
COURIERBOT_TTS_ENGINE=gemini
```

### Step 4: Update Code
Update the `synthesize_gemini_tts()` function in `assistant.py` to use OAuth2 credentials instead of API key authentication for Vertex AI access.

## Option B: Use Azure TTS (Current Fallback - Good Quality)

Azure TTS is already working with your current setup:
- Voice: `si-LK-SameeraNeural` (male, neural quality)
- No additional setup needed
- Good Sinhala pronunciation

This is the **current default** when Gemini fails.

## Option C: Use Standard Google TTS (Free Tier Available)

Standard Google voices are available with your current API key:
```env
COURIERBOT_TTS_ENGINE=google
```

Quality is lower than Neural/Gemini but it's free for up to 4M characters/month.

## TTS Priority Order

The current code tries TTS engines in this order:
1. **Gemini 2.5 Pro TTS** (if API permissions work)
2. **Azure Neural TTS** (fallback - currently working)

## Voice Options for Gemini TTS

When Gemini is working, you can choose these voices:
- **Achernar** (default) - Warm, professional
- **Achird** - Clear, articulate
- **Charon** - Deep, authoritative  
- **Fenrir** - Energetic
- **Kore** - Gentle, calm
- **Puck** - Friendly, approachable

Set in `.env`:
```env
GEMINI_TTS_VOICE=Achernar
```

## Testing

Test the current TTS configuration:
```bash
python quick_voice_check.py
```

Test Gemini directly:
```bash
python test_gemini_direct.py
```
