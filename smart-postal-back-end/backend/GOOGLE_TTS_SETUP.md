# Google Cloud TTS Setup - Better Sinhala Voices!

Google Cloud TTS has **MUCH better Sinhala voices** than Azure. The voices sound more natural and native-like.

## Why Google Cloud TTS?

- **Better pronunciation**: Trained on native Sinhala speakers
- **More natural**: WaveNet and Neural2 voices sound human-like
- **Free tier**: **4 million characters/month FREE** (vs Azure's 500K)
- **Cost**: Only $4 per 1M characters for Standard, $16 for WaveNet (after free tier)

**Typical query**: "Karunakara tracking number eka danaganeemata puluwanda?" = ~50 characters
**You can do 80,000 queries/month FREE!**

## Available Sinhala Voices

1. **si-LK-Wavenet-A** (Female) - Most natural female voice
2. **si-LK-Wavenet-B** (Male) - **RECOMMENDED** - Most natural male voice
3. **si-LK-Standard-A** (Female) - Basic quality
4. **si-LK-Standard-B** (Male) - Basic quality

## Setup Steps

### 1. Enable Google Cloud TTS API

1. Go to https://console.cloud.google.com/
2. Select your project (same one you use for Gemini)
3. Go to **APIs & Services** > **Library**
4. Search for "Text-to-Speech API"
5. Click **Enable**

### 2. Get API Key

You can use the same API key you're already using for Gemini!

**Your Gemini API key**: `AIzaSyAQKIovWWRA5XtKD0Uei2eujmo6pjMWQWQ`

Just enable the Text-to-Speech API on the same project, and this key will work!

### 3. Update Configuration

Already done in `backend/config/.env`:

```env
GOOGLE_CLOUD_TTS_API_KEY=AIzaSyAQKIovWWRA5XtKD0Uei2eujmo6pjMWQWQ
COURIERBOT_TTS_ENGINE=google
```

## Quick Test

Run this Python script to test:

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient(
    client_options={"api_key": "AIzaSyAQKIovWWRA5XtKD0Uei2eujmo6pjMWQWQ"}
)

# Set the text
synthesis_input = texttospeech.SynthesisInput(text="මගේ පැකේජය ගැන කියන්න")

# Male voice
voice = texttospeech.VoiceSelectionParams(
    language_code="si-LK",
    name="si-LK-Wavenet-B",  # Male
    ssml_gender=texttospeech.SsmlVoiceGender.MALE
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.95,  # Slightly slower
    pitch=-1.0  # Slightly lower pitch
)

response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

with open("test_google_tts.mp3", "wb") as out:
    out.write(response.audio_content)
    print(f"Generated {len(response.audio_content)} bytes")
```

## Cost Comparison

**For 10,000 queries/month** (~50 chars each = 500K chars total):

- **Google WaveNet**: FREE (under 4M free tier)
- **Azure Neural**: FREE (under 500K free tier) - but you'd exceed it!
- **gTTS**: FREE but sounds robotic

**For 100,000 queries/month** (5M chars):

- **Google WaveNet**: $16 (1M excess × $16)
- **Azure Neural**: $80 (4.5M excess × ~$18)
- **gTTS**: FREE

## Voice Quality Ranking

1. **🥇 Google si-LK-Wavenet-B** - Most natural, sounds like native speaker
2. **🥈 Azure si-LK-SameeraNeural** - Good but sounds slightly foreign
3. **🥉 gTTS** - Robotic, female only

##Implementation Status

✅ Google Cloud TTS library installed
✅ Configuration added to .env
❌ Need to add Google TTS code to assistant.py (both endpoints)

I can help you add the code if you want to switch!
