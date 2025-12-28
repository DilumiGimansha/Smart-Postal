# 🎤 Sinhala Voice Assistant Integration Guide

## Overview
The Sinhala Voice Assistant has been successfully integrated into the Smart-Postal system as a **separate conversational AI service** that complements the existing biometric voice verification.

## 🎯 Two Voice Systems - Different Purposes

### 1. **Voice Biometric Authentication** (Existing)
- **Purpose**: Security & identity verification
- **Technology**: Resemblyzer (256-dim embeddings), anti-spoofing
- **Location**: `utils/voice_banking.py`
- **Endpoints**: `/api/voice/enroll`, `/api/voice/verify`

### 2. **Sinhala Voice Assistant** (New)
- **Purpose**: Customer service & package queries
- **Technology**: Whisper STT, Gemini LLM
- **Location**: `services/sinhala_assistant/`
- **Endpoints**: `/api/assistant/query/voice`, `/api/assistant/query/text`

---

## 📂 Integration Structure

```
backend/
├── services/
│   └── sinhala_assistant/          # 🆕 Core assistant service
│       ├── __init__.py
│       ├── courier_bot.py          # Main bot logic (from your folder)
│       └── .env                    # GEMINI_API_KEY
│
├── api/routes/
│   └── assistant.py                # 🆕 API endpoints
│
├── utils/
│   └── sinhala_voice.py            # 🆕 Whisper STT wrapper
│
├── data/assistant/                 # 🆕 Mock data (for testing)
│   ├── mock_db.json
│   └── pickups.json
│
├── main.py                         # ✏️ Updated: includes assistant router
└── requirements.txt                # ✏️ Updated: added Gemini, Whisper, etc.
```

---

## 🔧 Setup Instructions

### 1. **Install Dependencies**
```powershell
cd smart-postal-back-end\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**New dependencies added:**
- `google-generativeai` - Gemini LLM
- `openai` + `openai-whisper` - Speech-to-text
- `SpeechRecognition` - Fallback STT
- `gTTS` + `pygame` - Text-to-speech (optional)
- `pydub` - Audio processing

### 2. **Configure API Keys**

Create/update `services/sinhala_assistant/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional: for better Whisper STT
```

Or add to main `config/.env`:
```env
# Existing keys...
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. **Start the Server**
```powershell
python run.py
```

---

## 📡 API Endpoints

### Voice Query (Audio)
```http
POST /api/assistant/query/voice
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: audio_file.wav
tracking_id: TRK001 (optional)
```

**Response:**
```json
{
  "success": true,
  "response_text": "Parcel eka Kurunegala thiyenawa, rider Saman langa.",
  "transcript": "මගේ පාර්සලය කොහෙද?",
  "response_audio": null,
  "error": null
}
```

### Text Query (Testing)
```http
POST /api/assistant/query/text
Content-Type: application/json
Authorization: Bearer {token}

{
  "text": "TRK001 koheda?",
  "tracking_id": "TRK001"
}
```

### Reset Conversation
```http
POST /api/assistant/reset-conversation
Authorization: Bearer {token}
```

### Get User Packages
```http
GET /api/assistant/packages
Authorization: Bearer {token}
```

---

## 🌐 Frontend Integration

The assistant UI has been added to `frontend_test/index.html`:

**Features:**
- 🎙️ Voice query upload (audio files)
- 💬 Text query input (for testing)
- 🤖 Response display with transcript
- 🔄 Conversation reset
- 🇱🇰 Sinhala/Singlish support

**Location:** Section 6 (after Face Recognition)

---

## 🧪 Testing

### Test Credentials
- Email: `test@example.com`
- Password: `Password123`

### Test Scenarios

#### 1. **Package Tracking**
**Voice/Text:** "TRK001 koheda?" or "මගේ පාර්සලය කොහෙද?"  
**Expected:** Status, location, rider name, delivery date

#### 2. **Shipping Rates**
**Voice/Text:** "Colombo idan Kandy ta kilo 2 kata kiyada?"  
**Expected:** "Rupiyaal 450"

#### 3. **Reschedule Delivery**
**Voice/Text:** "December 5 ta reschedule karanna"  
**Expected:** Confirmation of reschedule

---

## 🎤 How It Works

### Voice Query Flow
```
1. User uploads audio file
   ↓
2. Whisper STT transcribes to text
   ↓
3. Text sent to Gemini LLM (via courier_bot.py)
   ↓
4. Bot processes query, calls functions (get_tracking_status, etc.)
   ↓
5. Response returned in Sinhala
   ↓
6. Frontend displays response
```

### Key Components

#### `courier_bot.py`
- Gemini LLM integration
- Function calling (tracking, rates, reschedule)
- Context memory
- Sinhala prompt engineering

#### `sinhala_voice.py`
- Whisper STT integration
- Audio file handling
- Multiple STT fallbacks (OpenAI API → Local Whisper → SpeechRecognition)

#### `assistant.py` (routes)
- FastAPI endpoints
- User authentication
- Database integration
- Error handling

---

## 🔗 Connecting to Real Data

Currently uses mock data (`data/assistant/mock_db.json`). To connect to real database:

### Option 1: Update courier_bot.py
```python
# In courier_bot.py, modify get_tracking_status()
def get_tracking_status(tracking_id: str) -> Dict[str, Any]:
    # Instead of reading mock_db.json:
    from models.order import Order
    from models.database import SessionLocal
    
    db = SessionLocal()
    order = db.query(Order).filter(Order.tracking_id == tracking_id).first()
    db.close()
    
    if order:
        return {
            "status": order.status,
            "location": order.delivery_address,
            "estimated_delivery": str(order.created_at)
        }
    return None
```

### Option 2: Use API endpoint
The `/api/assistant/packages` endpoint already connects to real database.

---

## 🚀 Production Considerations

### 1. **API Key Security**
- Store GEMINI_API_KEY in environment variables
- Never commit `.env` files
- Use Azure Key Vault or AWS Secrets Manager

### 2. **Whisper Performance**
- OpenAI API: Fast, cloud-based, costs money
- Local Whisper: Free, slower, requires GPU
- SpeechRecognition: Fallback, limited Sinhala support

### 3. **Rate Limiting**
- Gemini API: 60 requests/minute (free tier)
- OpenAI Whisper: Pay per minute of audio
- Consider caching responses for common queries

### 4. **Error Handling**
- Graceful fallbacks if STT/LLM fails
- Timeout handling (30s max for voice queries)
- Retry logic with exponential backoff

---

## 🐛 Troubleshooting

### Assistant not responding
1. Check GEMINI_API_KEY is set
2. Verify Gemini model access: `check_models.py`
3. Check logs: `[courierbot] Using Gemini model...`

### STT not working
1. Ensure audio file format is supported (WAV, MP3, M4A)
2. Check OPENAI_API_KEY if using API
3. Install local Whisper: `pip install openai-whisper`

### Import errors
1. Restart server after installing dependencies
2. Check `sys.path` includes `services/sinhala_assistant`
3. Verify `__init__.py` exists in all folders

---

## 📝 Future Enhancements

### Phase 1 (Current)
- ✅ Voice query processing
- ✅ Text query for testing
- ✅ Basic package tracking
- ✅ Mock data integration

### Phase 2 (Planned)
- 🔲 Real-time voice recording (browser mic)
- 🔲 TTS response playback (gTTS/Azure TTS)
- 🔲 Full database integration
- 🔲 Multi-language support (Tamil, English)

### Phase 3 (Future)
- 🔲 Voice authentication + assistant combo
- 🔲 Proactive delivery notifications
- 🔲 Sentiment analysis
- 🔲 Voice analytics dashboard

---

## 📚 Documentation Files

From your original assistant folder:
- `README.md` - Original assistant documentation
- `funtionspecification.md` - Function specifications
- `CONVERSATION_IMPROVEMENTS.md` - Prompt engineering
- `AZURE_TTS_SETUP.md` - Azure TTS integration guide
- `DEEPSEEK_SETUP.md` - Alternative LLM setup

---

## 🎓 Key Differences from Biometric Voice

| Feature | Biometric Voice | Sinhala Assistant |
|---------|----------------|-------------------|
| **Purpose** | Authentication | Customer service |
| **Input** | Any voice sample | Sinhala questions |
| **Output** | Match score | Text response |
| **Model** | Resemblyzer | Gemini + Whisper |
| **Security** | Critical | Informational |
| **Storage** | Voice embeddings | Conversation logs |
| **Real-time** | Yes | No (async) |

---

## 📞 Support

For issues with:
- **Biometric voice**: Check `VOICE_VERIFICATION_BANKING_GRADE.md`
- **Sinhala assistant**: Check this file + original `README.md`
- **Integration**: Check `main.py` logs

---

## ✅ Integration Checklist

- [x] Folder structure created
- [x] Files copied to appropriate locations
- [x] Dependencies added to requirements.txt
- [x] API routes created
- [x] Main app updated (router included)
- [x] Frontend UI added
- [x] JavaScript functions implemented
- [x] Documentation created

**Status:** ✅ Ready for testing!

---

**Next Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Add GEMINI_API_KEY to `.env`
3. Start server: `python run.py`
4. Open frontend: `frontend_test/index.html`
5. Login and test assistant queries!
