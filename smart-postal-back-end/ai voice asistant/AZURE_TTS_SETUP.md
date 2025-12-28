# Azure TTS Setup for Better Sinhala Pronunciation

## Why Azure TTS?
- **Much better pronunciation** - Natural neural voices for Sinhala
- **Very affordable** - $1 per 1 million characters (500,000 free monthly)
- **Available voices**: 
  - `si-LK-ThiliniNeural` (Female, natural)
  - `si-LK-SameeraNeural` (Male, natural)

## Setup Steps

### 1. Create Free Azure Account
1. Go to https://azure.microsoft.com/free/
2. Sign up with your email
3. Get **$200 free credit** for 30 days
4. After free trial: **500,000 characters FREE per month**

### 2. Create Speech Service Resource
1. Go to Azure Portal: https://portal.azure.com
2. Click "Create a resource"
3. Search for "Speech"
4. Click "Speech" → "Create"
5. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: Create new (e.g., "courier-bot-rg")
   - **Region**: Select closest (e.g., "Southeast Asia" or "East US")
   - **Name**: e.g., "courier-bot-speech"
   - **Pricing tier**: Free F0 (500K chars/month) or Standard S0
6. Click "Review + Create" → "Create"

### 3. Get Your API Keys
1. After creation, go to your Speech resource
2. Click "Keys and Endpoint" in left menu
3. Copy:
   - **KEY 1** (your API key)
   - **Region** (e.g., "eastus" or "southeastasia")

### 4. Install Azure SDK
```powershell
cd "c:\Users\dinid\OneDrive\Desktop\ai voice asistant"
.\.venv\Scripts\python.exe -m pip install azure-cognitiveservices-speech>=1.38.0
```

### 5. Configure Environment Variables
Add to your `.env` file:
```env
# Azure TTS (Better Sinhala pronunciation)
AZURE_SPEECH_KEY=your_key_from_step_3
AZURE_SPEECH_REGION=southeastasia
COURIERBOT_TTS_ENGINE=azure
```

### 6. Test It
Run the bot - you'll hear much better Sinhala pronunciation!

## Comparison

| Feature | gTTS (Current) | Azure TTS |
|---------|---------------|-----------|
| Pronunciation | Robotic | Natural |
| Voice Quality | Low | High |
| Sinhala Support | Basic | Excellent |
| Cost | Free | $1/1M chars |
| Free Tier | Unlimited | 500K/month |
| Setup | None | 5 minutes |

## Switching Back to gTTS
Remove or comment out in `.env`:
```env
# COURIERBOT_TTS_ENGINE=azure
```
Or set to:
```env
COURIERBOT_TTS_ENGINE=gtts
```

## Voice Options
To use male voice instead of female, edit `courier_bot.py` line:
```python
speech_config.speech_synthesis_voice_name = "si-LK-SameeraNeural"  # Male voice
```
