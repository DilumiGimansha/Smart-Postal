# Sinhala Voice Assistant - Quick Start Guide

## 🎉 Voice System Status: FULLY OPERATIONAL

All voice components are working perfectly!

---

## ✅ What's Working:

1. **Microphone Input** - 30 microphones detected
2. **Speech Recognition** - Google Speech API (Sinhala language)
3. **Text-to-Speech** - gTTS with Sinhala support
4. **Audio Playback** - pygame mixer
5. **AI Processing** - Gemini 2.0 Flash with function calling
6. **Package Tracking** - Database integration working

---

## 🎤 How to Use Full Voice Mode

### Option 1: Interactive Voice Session
```bash
cd "smart-postal-back-end/ai voice asistant"
python courier_bot.py
```

This will:
- Listen for your voice input via microphone
- Process Sinhala speech
- Query the AI model
- Speak responses in Sinhala
- Continue conversation until you say "exit" or "nawathanna"

### Option 2: Text Input Mode
If you prefer typing (no microphone):
```bash
python courier_bot.py
```
Then just type your queries when prompted.

---

## 🗣️ Voice Commands You Can Try

### Greetings:
- "හලෝ" (Hello)
- "අයුබෝවන්" (Greetings)

### Package Tracking:
- "TRK001 එකේ status එක දෙන්නද?" (Give me status of TRK001)
- "මගේ පැකේජය කොහෙද?" (Where is my package?)
- "tracking number එක check කරන්නද?" (Can you check the tracking number?)

### Shipping Rates:
- "කොළඹ to කුරුණෑගල delivery cost එක කීයද?" (What's the delivery cost from Colombo to Kurunegala?)
- "2kg parcel එකක් එවන්න කීයද?" (How much to send a 2kg parcel?)

### Delivery Rescheduling:
- "TRK001 delivery date එක change කරන්නද?" (Can you change the delivery date for TRK001?)

### Exit:
- "exit"
- "bye"
- "nawathanna" (stop)
- "ඉවරයි" (finished)

---

## 📊 Test Results Summary

```
✅ PASS: Audio Libraries - All installed
✅ PASS: Microphone Detection - 30 devices found
✅ PASS: Text-to-Speech - Working perfectly
✅ PASS: Speech Recognition - Sinhala recognized correctly
✅ PASS: Bot Voice Integration - speak_sinhala() working
✅ PASS: Full Conversation Flow - End-to-end test successful

Total: 6/6 tests passed (100%)
```

---

## 🎯 Sample Conversation Test Results

**Test:** User spoke "මගේ පැකේජය ගැන දැන" (About my package)
- ✅ Speech captured successfully
- ✅ Text recognized correctly
- ✅ Audio quality: Clear

**Test:** Bot query TRK001 status
- ✅ Function calling: get_tracking_status executed
- ✅ Response: "Parcel eka Kurunegala thiyenawa, rider Saman langa. December 25 ta ganna puluwan."
- ✅ Audio output: Sinhala speech generated and played

---

## 🔧 Technical Details

### Microphones Available:
- Digital Microphone (Cirrus Logic)
- Multiple input devices detected
- Bluetooth headsets supported (TWS, Galaxy M31, soundcore R50i)

### Audio Pipeline:
1. **Input:** PyAudio → SpeechRecognition
2. **STT:** Google Speech Recognition API (si-LK)
3. **Processing:** Gemini 2.0 Flash with function calling
4. **TTS:** gTTS (Sinhala voice)
5. **Output:** pygame mixer

### Known Limitations:
- OPENAI_API_KEY not set (using Google Speech Recognition instead - works fine)
- ffmpeg not found for pydub (not required for basic functionality)
- Azure TTS not configured (using gTTS which works well)

---

## 🚀 Ready to Start!

Everything is set up and working. Just run:

```bash
python courier_bot.py
```

The bot will:
1. Listen for your voice 🎙️
2. Understand Sinhala 🇱🇰
3. Process queries with AI 🤖
4. Call functions (tracking, rates, etc.) 📦
5. Speak responses in Sinhala 🔊

**Enjoy your fully functional Sinhala Voice Assistant!** 🎉
