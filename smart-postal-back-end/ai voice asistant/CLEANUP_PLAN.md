# Cleanup Plan - Remove Unused API Code

## Current Status
You have code for 4 LLM providers, but only using **Gemini**:
- ✅ **Gemini** - KEEP (currently used)
- ❌ **Groq** - REMOVE (models decommissioned)
- ❌ **DeepSeek** - REMOVE (requires $5 deposit)
- ❌ **OpenRouter** - REMOVE (free tier removed)

## What Can Be Safely Removed

### 1. Environment Variables (.env file)
**REMOVE these lines (lines 5-20):**
```env
# OpenRouter API (truly free models - NO CREDIT CARD NEEDED!)
# Get free key from: https://openrouter.ai/keys
# Try these models: qwen/qwen-2-7b-instruct:free or google/gemini-flash-1.5
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=qwen/qwen-2-7b-instruct:free
COURIERBOT_USE_OPENROUTER=false

# DeepSeek API (generous free tier - RECOMMENDED)
# Get free key from: https://platform.deepseek.com/
# NOTE: DeepSeek requires adding credits ($5 minimum) even for free tier
DEEPSEEK_API_KEY=sk-16dc4291ed7f46be8651b36aa46131e6
COURIERBOT_USE_DEEPSEEK=false

GROQ_API_KEY=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
# Disable Groq (models decommissioned)
COURIERBOT_USE_GROQ=false
```

**KEEP only:**
```env
GEMINI_API_KEY=AIzaSyAQKIovWWRA5XtKD0Uei2eujmo6pjMWQWQ
COURIERBOT_MODEL=gemini-2.0-flash-exp
```

### 2. Dependencies (requirements.txt)
**REMOVE these lines:**
```
openai>=1.50.0
groq>=0.9.0
```

**KEEP:**
```
google-generativeai>=0.8.0
python-dotenv>=1.0.1
SpeechRecognition>=3.10.0
gTTS>=2.5.4
pydub>=0.25.1
openai-whisper>=20231117
torch>=2.0.0
numpy<2.0.0
pygame>=2.5.0
```

### 3. Code in courier_bot.py

**REMOVE these sections:**

#### A. Global variables (around line 113-116)
```python
GROQ_CLIENT: Optional["GroqClient"] = None
DEEPSEEK_CLIENT: Optional["OpenAI"] = None
OPENROUTER_CLIENT: Optional["OpenAI"] = None
OPENAI_CLIENT: Optional["OpenAI"] = None
```

#### B. Client getter functions (lines ~340-430)
- `get_groq_client()` - entire function
- `get_deepseek_client()` - entire function  
- `get_openrouter_client()` - entire function

#### C. Turn handler functions (lines ~800-1100)
- `handle_groq_turn()` - entire function (~40 lines)
- `handle_deepseek_turn()` - entire function (~120 lines)
- `handle_openrouter_turn()` - entire function (~120 lines)

#### D. In `initialize_model()` function (lines ~370-430)
Remove the OpenRouter/DeepSeek/Groq checking logic, keep only:
```python
def initialize_model() -> Any:
    """Initialize and return Gemini model."""
    load_env()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")
    
    # Configure Gemini
    tools = build_tools()
    model_name = resolve_model_name()
    safety_settings = [...]
    
    return genai.GenerativeModel(...)
```

#### E. In `handle_model_turn()` function (lines ~700-730)
Simplify to only call `handle_gemini_turn()`:
```python
def handle_model_turn(model: Any, chat: Any, user_text: str) -> Tuple[str, Any]:
    """Send user input to Gemini and resolve any tool calls."""
    return handle_gemini_turn(model, chat, user_text)
```

#### F. In `chat_session()` function (lines ~1130-1140)
Remove the client type checking:
```python
def chat_session() -> None:
    """Main console loop."""
    model = initialize_model()
    chat = model.start_chat(history=[])  # Only Gemini
    # ... rest of function
```

## Benefits After Cleanup

1. **Simpler codebase**: ~400 lines removed
2. **Fewer dependencies**: Remove openai, groq packages
3. **Easier maintenance**: Only one API to manage
4. **Clearer code**: No confusing multi-provider logic
5. **Smaller file**: courier_bot.py: 1188 lines → ~780 lines

## How to Apply Cleanup

**Option 1: I can do it for you** (Recommended)
Say "clean up the code" and I'll remove all unused code automatically.

**Option 2: Manual cleanup**
1. Delete the sections listed above
2. Test the bot still works
3. Remove unused packages: `pip uninstall openai groq`

## What to Keep

✅ All Gemini-related code
✅ All speech recognition (Whisper, SpeechRecognition)
✅ All TTS code (gTTS, Azure TTS)
✅ All courier functions (tracking, rates, reschedule)
✅ All helper functions
✅ pygame for audio playback
✅ mock_db.json

## Estimated Changes

- **.env**: 16 lines removed
- **requirements.txt**: 2 lines removed  
- **courier_bot.py**: ~400 lines removed
- **Total**: ~420 lines cleaner

Would you like me to proceed with the cleanup?
