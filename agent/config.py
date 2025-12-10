from __future__ import annotations
import os

# Which Gemini model to use
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# ⚠️ LOCAL ONLY: put your real Gemini API key here.
# Do NOT commit this file to GitHub with the real key.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Simple safety filter for generated tests
FORBIDDEN_IMPORTS = [
    "os.system",
    "subprocess",
    "requests",
    "socket",
    "shutil.rmtree",
]
