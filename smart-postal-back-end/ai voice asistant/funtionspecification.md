# Project Specification: Sinhala AI Voice Assistant for Courier System

## 1. Project Overview
**Goal:** Build a voice-first conversational agent capable of handling courier logistics queries in Sinhala (and "Singlish").
**Primary User:** Courier customers and drivers.
**Language:** Sinhala (Native & Romanized/Singlish).
**Core Capability:** The assistant handles Tracking, Rate Calculation, and Delivery Scheduling via voice interactions.

---

## 2. Technology Stack
* **LLM / Intelligence:** Google Gemini 3.0 Pro (via Vertex AI or Studio API).
* **Speech-to-Text (STT):** OpenAI Whisper (v3) OR Azure Speech Service (Sinhala model).
* **Text-to-Speech (TTS):** Microsoft Azure Neural TTS (Voice: `si-LK-ThiliniNeural` or similar).
* **Backend Runtime:** Python (FastAPI) or Node.js.
* **Orchestration:** LangChain or Native Function Calling.

---

## 3. Architecture & Data Flow
1.  **Audio Input:** User speaks in Sinhala.
2.  **STT Layer:** Transcribes audio to text.
3.  **LLM Processing (Gemini 3):**
    * Receives text input + conversation history.
    * Determines intent (Track, Rate, Schedule).
    * **CRITICAL:** Executes **Function Calls** (Tools) to fetch real-time data from the Courier Backend.
4.  **Data Retrieval:** Backend returns JSON data (e.g., `{"status": "In Transit", "location": "Kandy"}`).
5.  **Response Generation:** Gemini 3 generates a natural Sinhala response using the retrieved data.
6.  **TTS Layer:** Converts the Sinhala text response to audio.
7.  **Output:** Plays audio to the user.

---

## 4. Gemini 3 Configuration & System Prompt

### Model Settings
* **Model:** `gemini-3.0-pro`
* **Temperature:** 0.3 (Low temperature for factual accuracy in logistics).
* **Tools:** Enable Function Calling.

### System Prompt (Persona)
> You are a helpful customer support AI for a Sri Lankan courier service.
> * **Language:** You speak natural, polite Sinhala. You can understand "Singlish" (Sinhala words typed/spoken in English letters) but always reply in standard spoken Sinhala style (not written/literary style).
> * **Behavior:** Be concise. Courier customers are in a hurry.
> * **Privacy:** Never reveal driver phone numbers unless explicitly authorized by the data.
> * **Fallback:** If you do not understand the Tracking ID, ask the user to repeat it clearly or type it.

---

## 5. Function Definitions (Tools)

The AI Agent must implement these function schemas for Gemini to call.

### A. `get_tracking_status`
**Description:** Fetches the current location and status of a package.
**Parameters:**
* `tracking_id` (string, required): The tracking number (e.g., "TRK-100").

### B. `calculate_shipping_rate`
**Description:** Calculates the cost of sending a package.
**Parameters:**
* `origin_city` (string, required): Pickup location.
* `destination_city` (string, required): Drop-off location.
* `weight_kg` (float, required): Weight of the package.

### C. `reschedule_delivery`
**Description:** Updates the preferred delivery date/time.
**Parameters:**
* `tracking_id` (string, required).
* `new_date` (string, required): Format YYYY-MM-DD.

---

## 6. Example Conversation Flow (Logic Reference)

**User (Audio):** "Mage package eka koheda thiyenne? Number eka TRK555." (Where is my package? Number is TRK555.)

**Step 1: STT Output:** "Mage package eka koheda thiyenne? Number eka TRK555."

**Step 2: Gemini Tool Call:**
```json
{
  "name": "get_tracking_status",
  "args": {
    "tracking_id": "TRK555"
  }
}
Step 3: Backend API Result:

JSON

{
  "status": "Out for Delivery",
  "rider_name": "Kamal",
  "estimated_time": "14:00"
}
Step 4: Gemini Final Response (Sinhala): "Obage parcel eka rider Kamal langa thiyenne. Ada hawasa 2.00 ta paman labewi." (Your parcel is with rider Kamal. You will receive it around 2:00 PM today.)