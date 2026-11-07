import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.0-flash")

prompt = """
Create one original Roblox-style YouTube Shorts story.
Duration: 30 seconds.
Include:
1. A strong opening hook.
2. A funny or surprising story.
3. A satisfying ending.
Return the story as JSON with title, scenes, and narration.
"""

response = model.generate_content(prompt)

print(response.text)
