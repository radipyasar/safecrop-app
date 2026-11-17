"""Day 1 check: does the Gemini key work?  Run in backend/:  python scripts/check_gemini.py
The key is read from backend/.env (GEMINI_API_KEY). It is never printed."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
print(model, "->", client.models.generate_content(model=model, contents="Say hi in five words.").text)
