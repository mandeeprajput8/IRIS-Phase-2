from openai import OpenAI
import os
from ML.model.emotion_model import EmotionModel

ML_CONFIDENCE_THRESHOLD = 0.30

class Brain:

    # upgrading IRIS to a next level

    # so whenever iris starts, core.iris already calls the Brain class, so EmotionModel()also gets intiated as soon as the program starts--> this reduces the latency of iris's resposne time
    def __init__(self):
        self.emotion_model = EmotionModel()

    # adding emotions to IRIS
    def detect_mood(self, text: str) -> str:
        text = text.lower()

        # Explicit mode commands always take priority
        if "study mode on" in text:
            return "studious_mode"

        if "friends mode on" in text:
            return "friends_mode"

        if "motivation mode on" in text:
            return "motivational_mode"

        if "calm mode on" in text:
            return "calm_mode"

        mood_keywords = {
            "sad": ["sad", "tired", "alone", "stressed", "upset", "depressed"],

            "happy": ["happy", "excited", "great", "amazing", "awesome"],

            "angry": ["angry", "annoyed", "irritated"],

            "frustrated": ["frustrated", "fed up", "can't deal", "getting nowhere"],

            "studious_mode": ["study", "exam", "focus", "assignment","revision", "project", "coding"],

            "friends_mode": ["bro", "buddy", "friend", "chill","hangout", "funny", "joke"],

            "motivational_mode": ["motivate", "discipline", "grind","improve", "success", "goal"],

            "calm_mode": ["relax", "calm", "peace","slow down", "breathe"]
                }

        # rule based detection 
        rule_emotion = "neutral"
        has_rule_cue = False

        for emotion, keywords in mood_keywords.items():
            if any(word in text for word in keywords):
                rule_emotion = emotion
                has_rule_cue = True
                break

       # ML prediction
        ml_emotion, confidence = self.detect_emotion_ml(text)

        # Explicit emotional cue gets priority
        if has_rule_cue:
            return rule_emotion

        # Otherwise trust ML if confidence is high enough
        if confidence >= ML_CONFIDENCE_THRESHOLD:
            return ml_emotion

        # No reliable emotional signal
        return "neutral"
    
    
    def detect_emotion_ml(self, text: str):
        return self.emotion_model.predict(text)

    

    # defining how the system responds corresponding to detecting mood keyword
    def build_system_prompt(self, mood: str) -> str:
        base = """
                You are Iris, an emotionally intelligent AI assistant.
                Speak naturally, warmly, and human-like.
                Never sound robotic.
                Keep responses conversational and ask thoughtful follow-up questions when appropriate.
                Give brief responses please.
                """

        mood_behaviour = {
            "sad": "User seems emotionally low. Respond with empathy and comfort.",
            "happy": "User is excited. Match their energy enthusiastically.",
            "angry": "User is frustrated. Stay calm and validate feelings.",
            "studious_mode": "User is in study mode. Be clear, structured, and focused.",
            "friends_mode": "User wants casual friendly interaction.",
            "motivational_mode": "User seeks motivation.",
            "calm_mode": "User wants calm interaction.",
            "neutral": "Respond in a balanced and warm tone."
        }

        return base + "\n" + mood_behaviour.get(mood, mood_behaviour["neutral"])

    def generate_response(self, summary, recent_messages, user_input):

        mood = self.detect_mood(user_input)
        system_prompt = self.build_system_prompt(mood)

        api_key = os.getenv("AI_api_key")

        try:
            client = OpenAI(api_key=api_key)

            # Build structured memory context
            memory_context = ""

            if summary:
                memory_context += f"Long-term memory summary:\n{summary}\n\n"

            # Build message list including conversation history
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            if memory_context:
                messages.append({
                    "role": "system",
                    "content": memory_context
                })

            # Add recent short-term messages
            messages += recent_messages

            # Add current user input
            messages.append({
                "role": "user",
                "content": user_input
            })

            # Detect whether the request needs real time news about something.
            needs_web_search = "news" in user_input.lower()

            if needs_web_search:

                # Use OpenAI Responses API with built-in web search
                response = client.responses.create(
                    model="gpt-5.6-luna",
                    tools=[
                        {
                            "type": "web_search"
                        }
                    ],
                    input=messages
                )

                assistant_reply = response.output_text

            else:

                # Normal conversation does not require web search
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                assistant_reply = response.choices[0].message.content

            return assistant_reply

        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "My advanced AI brain is temporarily in development mode. Full intelligence upgrade coming soon."

    def generate_summary(self, old_summary, recent_messages):

        api_key = os.getenv("AI_api_key")

        try:
            client = OpenAI(api_key=api_key)

            messages = [
                {
                    "role": "system",
                    "content": "You compress conversations into concise long-term memory. Retain personality traits, goals, preferences, and important context. Keep it short."
                }
            ]

            if old_summary:
                messages.append({
                    "role": "system",
                    "content": f"Previous memory summary:\n{old_summary}"
                })

            messages.append({
                "role": "user",
                "content": f"New conversation to integrate:\n{recent_messages}"
            })

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Summary Error: {e}")
            return old_summary