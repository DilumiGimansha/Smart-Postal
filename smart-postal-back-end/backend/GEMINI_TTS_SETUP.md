# How to Enable Gemini Pro TTS (Achernar Voice)

## Problem
Gemini TTS models (like gemini-2.5-pro-tts) use Vertex AI backend, which requires:
- Active billing with valid payment method
- Service Account authentication (API keys aren't sufficient)

## Solution: Create Service Account

### Step 1: Create Service Account
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=582560921998
2. Click "CREATE SERVICE ACCOUNT"
3. Name: `tts-service-account`
4. Click "CREATE AND CONTINUE"

### Step 2: Grant Roles
Add these roles:
- ✅ **Cloud Text-to-Speech User** (roles/texttospeech.user)
- ✅ **Vertex AI User** (roles/aiplatform.user)

Click "CONTINUE" → "DONE"

### Step 3: Create Key
1. Click on the service account you just created
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Download the JSON file

### Step 4: Configure in Your Project
1. Save the JSON file to:
   `smart-postal-back-end/backend/config/service-account-key.json`

2. Update `.env`:
   ```env
   # Service Account for Gemini TTS
   GOOGLE_APPLICATION_CREDENTIALS=config/service-account-key.json
   COURIERBOT_TTS_ENGINE=gemini
   ```

3. The code will use the service account automatically when the file exists.

### Step 5: Verify Billing
1. Go to: https://console.cloud.google.com/billing
2. Ensure billing account is linked to project 582560921998
3. Ensure you have a valid payment method
4. Gemini TTS is paid (no free tier), but very affordable:
   - ~$0.10 per 1 million characters (10x cheaper than shown in your screenshot!)

## Alternative: Use Neural2 Voices (If Available)

If Gemini TTS is too expensive or complex, try Neural2 voices:
- Same quality level as Gemini TTS
- Don't require Vertex AI permissions
- Use standard Text-to-Speech API
- Require billing but no service account

Update `.env`:
```env
COURIERBOT_TTS_ENGINE=google
```

Then we'll update the code to request Neural2 voices specifically.

## Fallback: Use Standard Voices (Free)

Already configured! Change `.env`:
```env
COURIERBOT_TTS_ENGINE=google
```

Standard voices work now (no billing, no service account needed).
Quality is lower but it's free and works immediately.

## Cost Comparison

| Voice Type | Quality | Free Tier | Paid Cost | Requires |
|------------|---------|-----------|-----------|----------|
| Standard | ⭐⭐ Basic | 4M chars/month | $4/1M after | Nothing |
| Neural2 | ⭐⭐⭐⭐ Good | None | $16/1M | Billing |
| Gemini Pro | ⭐⭐⭐⭐⭐ Best | None | $0.10/1M | Billing + Service Account |

**Your typical query:** ~50 characters
**100K queries/month:** 5M characters = **$0.50 with Gemini TTS!**

## Next Steps

**Option A:** Create service account (15 minutes) → Get Gemini TTS ⭐⭐⭐⭐⭐
**Option B:** Try Neural2 (2 minutes) → Good quality ⭐⭐⭐⭐
**Option C:** Use Standard (works now) → Basic quality ⭐⭐

Which would you prefer?
