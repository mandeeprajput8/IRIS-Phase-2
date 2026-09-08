import os

# Project Metadata

PROJECT_NAME = "Project Iris (Aurora Core)"
PROJECT_AUTHOR = "Mandeep Singh"
PROJECT_PHASE = "Phase 1"
PROJECT_COMPLETION_DATE = "01-03-2026"

# api keys

# api for openai
api_key = os.getenv("AI_api_key")


# Thinking phrases
thinking_phrases = [
    "One moment...",
    "Alright...",
    "Working on it.",
    "Just a second.",
    "Got it...",
    "On it."
]

# creator identity check
identity_trigger_phrases = [
"who am i",
"do you know who i am",
"who created you",
"what is my name",
"who is your creator"]

# ensuring she doesnt say yes for any other random name that the user says
creator_claim_phrases = [
"creator",
"made you",
"built you",
"created you"]