# DeepSeek API Setup (RECOMMENDED - No Quota Issues!)

## Why DeepSeek?
- ✅ **Generous free tier** - No daily limits like Gemini
- ✅ **No computing power needed** - Cloud API like Gemini/Groq
- ✅ **Excellent quality** - Competitive with GPT-4
- ✅ **Function calling support** - Works with your courier tools
- ✅ **Fast responses** - Better latency than Gemini free tier

## Quick Setup (2 minutes)

1. **Get Free API Key:**
   - Go to: https://platform.deepseek.com/
   - Sign up with email (free)
   - Navigate to "API Keys" section
   - Click "Create API Key"
   - Copy the key (starts with `sk-...`)

2. **Add to .env file:**
   ```
   DEEPSEEK_API_KEY=sk-your-key-here
   COURIERBOT_USE_DEEPSEEK=true
   ```

3. **Run the bot:**
   ```powershell
   & ".venv/Scripts/python.exe" courier_bot.py
   ```

4. **You should see:**
   ```
   [INFO] Using DeepSeek API (generous free tier, no quota limits)
   ```

## Troubleshooting

**438 Requests Error with Gemini:**
Your Gemini quota exhausted because of heavy testing. DeepSeek doesn't have this issue.

**Does DeepSeek need local computing power?**
No! It's a cloud API just like Gemini. Your computer only sends text and receives responses.

**Cost?**
Free tier is very generous. If you exceed it, pricing is much cheaper than OpenAI.

## Priority Order

The bot tries APIs in this order:
1. **DeepSeek** (if `COURIERBOT_USE_DEEPSEEK=true` and key set)
2. **Groq** (if `COURIERBOT_USE_GROQ=true` and key set) 
3. **Gemini** (fallback if above not available)

This ensures you always have a working API!
