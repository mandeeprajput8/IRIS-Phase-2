from datetime import datetime
import random
import time
from voice.tts import speak
from voice.stt import listen
from core.config import thinking_phrases
from core.config import identity_trigger_phrases
from core.config import creator_claim_phrases
from core.brain import Brain
from core.memory import Memory
from routing.command_router import CommandRouter
from services.spotify_services import SpotifyService
from services.web_services import WebService
import re 

class Iris:

    # fallback to OpenAI to advanced tasks
    # initialising classes Brain and Memory
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain()

        # injecting services into router, dependency injection
        self.router = CommandRouter(
            SpotifyService(),
            WebService()
        )

    # this function greets the user when we say the wake word
    def greet(self):
        identity = self.memory.get_identity()
        greeting_name = identity.get("greeting_name", "Mandeep")

        hour = datetime.now().hour
        if 5 <= hour < 12:
            speak(f"Good morning {greeting_name}.")
        elif 12 <= hour < 17:
            speak(f"Good afternoon {greeting_name}.")
        elif 17 <= hour < 21:
            speak(f"Good evening {greeting_name}.")
        else:
            speak(f"Hey {greeting_name}, It's pretty late, y'know?")

    def process_command(self, command):
        """
        Process a single text command without using
        the microphone or entering the voice conversation loop.
        """

        # try local command first
        handled = self.router.route(command)

        if handled:
            return "Command executed successfully!!!"


        # =====================================================
        # CREATOR IDENTITY CHECK
        # =====================================================

        command_lower = command.lower().strip()

        if any(
            phrase in command_lower
            for phrase in identity_trigger_phrases
        ):

            identity = self.memory.get_identity()

            creator_name = identity.get(
                "creator_name",
                "unknown"
            )

            response = (
                f"Of course I know you. "
                f"You are my creator, {creator_name}."
            )

            self.memory.add("user", command)
            self.memory.add("assistant", response)

            return response


        # =====================================================
        # CREATOR CLAIM CHECK
        # =====================================================

        if any(
            phrase in command_lower
            for phrase in creator_claim_phrases
        ):

            identity = self.memory.get_identity()

            creator_name = identity.get(
                "creator_name",
                "unknown"
            )

            # Check whether the actual creator's name
            # is present in the user's claim.
            if creator_name.lower() in command_lower:

                response = (
                    f"Yes. I was created by "
                    f"{creator_name}."
                )

            else:

                response = (
                    f"Nice try. But I was built by "
                    f"{creator_name}."
                )

            self.memory.add("user", command)
            self.memory.add("assistant", response)

            return response


        # Store user input in memory
        self.memory.add("user", command)

        # Build context from MySQL
        summary = self.memory.get_summary()
        recent_messages = self.memory.get_recent(limit=10)

        # Generate response using the existing Brain
        response = self.brain.generate_response(
            summary,
            recent_messages,
            command
        )

        # Store assistant response
        self.memory.add("assistant", response)

        # Auto-summarize every 5 messages
        count = self.memory.get_message_count()

        if count % 5 == 0:
            old_summary = self.memory.get_summary()
            recent_for_summary = self.memory.get_recent(limit=20)

            new_summary = self.brain.generate_summary(
                old_summary=old_summary,
                recent_messages=recent_for_summary
            )

            self.memory.update_summary(new_summary)
            self.memory.trim_conversations(keep_last=10)

        return response


"""    RUN THIS PORTION WHEN CHECKING WORKING OF IRIS's BACKEND SYSTEM USING iris_cli.py
    def run(self):

        while True:
            try:
                word = listen(timeout=4, phrase_time_limit=5)

                if word and "iris" in word.lower():
                    print(f"Heard: {word}")
                    print("Wake word detected!")
                    self.greet()

                    command = listen()
                    if not command:
                        continue

                    print(f"Heard: {command}")
                    speak(random.choice(thinking_phrases))

                    # Try handling locally first
                    handled = self.router.route(command)
                    if handled:
                        continue
                    
                    # asking iris who created her, creator identity check
                    if any(phrase in command.lower() for phrase in identity_trigger_phrases):

                        identity = self.memory.get_identity()

                        full_name = identity.get("creator_name", "unknown")
                        aliases_raw = identity.get("creator_aliases", "")
                        aliases = [name.strip().lower() for name in aliases_raw.split(",")]

                        chosen_name = random.choice([full_name] + aliases)

                        response = f"Of course I know you. You are my creator, {chosen_name}."

                        self.memory.add("assistant", response)
                        speak(response)
                        continue
                
                    # ensuring iris doesnt just nod yes for any name I speak    
                    if any(phrase in command for phrase in creator_claim_phrases):

                        # Extract capitalized names (possible proper names)
                        potential_names = re.findall(r'\b[A-Z][a-z]+\b', command)
                        full_name = identity.get("creator_name", "unknown")
                        allowed_names = [full_name.lower()]

                        for name in potential_names:
                            if name.lower() not in allowed_names:
                                response = f"Nice try. But I was built by {full_name}."
                                self.memory.add("assistant", response)
                                speak(response)
                                continue
                            
                        # If claim contains allowed name, affirm
                        if any(name in command for name in allowed_names):
                            response = f"Yes. I was created by {full_name}."
                            self.memory.add("assistant", response)
                            speak(response)
                            continue

                    last_interaction = time.time()

                    while True:
                        
                        #memory injection 

                        # store user input in memory
                        self.memory.add("user", command)
                        # BUILD CONTEXT FROM MYSQL
                        # identity = self.memory.get_identity()
                        summary = self.memory.get_summary()
                        recent_messages = self.memory.get_recent(limit=10)

                        # pass structured memory into brain
                        response = self.brain.generate_response(
                            summary, 
                            recent_messages,
                            command
                        )

                        # store assistant reply
                        self.memory.add("assistant", response)

                        # AUTO-SUMMARIZE EVERY 5 MSGS
                        count = self.memory.get_message_count()

                        if count % 5 == 0:
                            old_summary = self.memory.get_summary()
                            recent_for_summary = self.memory.get_recent(limit=20)

                            new_summary = self.brain.generate_summary(
                                old_summary=old_summary,
                                recent_messages=recent_for_summary
                            )

                            self.memory.update_summary(new_summary)
                            self.memory.trim_conversations(keep_last=10)

                        speak(response)

                        command = listen(timeout=4, phrase_time_limit=5)

                        if not command:
                            # auto-exit after 10 sec silence
                            if time.time() - last_interaction > 10:
                                speak("Conversation ended. Returning to standby.")
                                break
                            continue

                        if command.lower().strip() in ["stop", "exit"]:
                            speak("Got it, returning to stand by mode now.")
                            break

                        last_interaction = time.time()

                        handled = self.router.route(command)
                        if handled:
                            break

            except Exception as e:
                print(f"Assistant Error: {e}")


# For iris_cli.py compatibility
iris_instance = Iris()  # object created for iris class
run = iris_instance.run  # calling class via object and storing the working of it inside a variable for main.py comapatibility"""
