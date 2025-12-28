# CourierBot Enhancements for Better Conversations

## Improving Response Quality
Since Gemini models like 2.5 Pro cannot be fine-tuned by users, we rely on prompt engineering and context to shape responses. The updated `SYSTEM_PROMPT` now includes:
- Detailed persona instructions.
- Examples of natural Sinhala responses for common scenarios.
- Guidelines for tone and conciseness.

## Further Improvements
1. **Add More Sample Data:** Expand `mock_db.json` with more tracking IDs and varied statuses to test edge cases.
2. **Knowledge Base:** Create a `faqs.json` with common questions and answers, then add a tool to search it.
3. **Few-Shot Prompting:** Include more conversation examples in the system prompt.
4. **Temperature Adjustment:** Lower to 0.1 for more consistent, factual replies.
5. **User Feedback Loop:** Log conversations and manually review to refine the prompt.

## Testing
Run the bot with various queries like:
- "Mage parcel eka koheda?" (Where is my parcel?)
- "Rate eka kiyanna?" (How to calculate rate?)
- "Delivery date change karanna?" (How to reschedule?)

Monitor logs for response quality and iterate on the prompt.