from fastapi import APIRouter

from app_services.iris_service import iris_service
from voice.stt import listen
from voice.tts import speak
import random

router = APIRouter(
    prefix="/api",
    tags=["Voice"]
)


@router.post("/voice")
def voice_command():

    # Listen to user's microphone
    command = listen(
        timeout=5,
        phrase_time_limit=5
    )

    if not command:
        return {
            "heard": None,
            "response": None,
            "standby": False
        }

    # Check local voice commands BEFORE sending anything to the AI pipeline
    command_lower = command.lower().strip()

    if command_lower in ["stop", "exit", "sleep"]:

        response = "Okay Sir, returning to standby mode."

        return {
            "heard": command,
            "response": response,
            "standby": True
        }

    # Send recognised speech through the SAME IRIS command pipeline used by text
    response = iris_service.process_command(command)

    return {
        "heard": command,
        "response": response,
        "standby": False
    }

@router.post("/voice/speak")
def voice_speak(text: str):

    speak(text)

    return {
        "status": "spoken"
    }

# iris will greet the user with one of the following greeting messages
welcome_messages = [
    "Hello, Sir. What are we cooking today?",
    "Good to see you, Sir. What can I do for you?",
    "I'm ready, Sir. What's on your mind?",
    "Hello, Sir. How can I assist you today?",
    "Systems online. What shall we work on?"
]


@router.post("/voice/welcome")
def voice_welcome():

    welcome = random.choice(welcome_messages)

    speak(welcome)

    return {
        "response": welcome
    }

# IRIS reactivating greetings

@router.post("/voice/reactivate")
def voice_reactivate():

    speak("Loading IRIS core.")
    speak("Hello again, Sir. What are we doing now?")

    return {
        "response": "Hello again, Sir. What are we doing now?"
    }