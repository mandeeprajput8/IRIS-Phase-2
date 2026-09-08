import pickle
from pathlib import Path


class EmotionModel:

    def __init__(self):
        model_path = Path(__file__).parent / "emotion_model.pkl"

        with open(model_path, "rb") as file:
            saved_model = pickle.load(file)

        self.vectorizer = saved_model["vectorizer"]
        self.model = saved_model["model"]

    def predict(self, text):
        # Convert the new text using the trained TF-IDF vectorizer
        text_tfidf = self.vectorizer.transform([text])

        # Predict the emotion
        emotion = self.model.predict(text_tfidf)[0]

        # Get confidence scores
        probabilities = self.model.predict_proba(text_tfidf)[0]
        confidence = max(probabilities)

        return emotion, confidence


# inference testing
# if __name__ == "__main__":
#     emotion_model = EmotionModel()

#     test_sentences = [
#         "I've been smiling all day because things finally worked out.",
#         "I got the job I really wanted and I'm absolutely thrilled.",
#         "My friend surprised me today and it made my whole day.",
        
#         "I don't know why, but I just haven't felt like myself lately.",
#         "Things have been really difficult recently and I feel drained.",
#         "I miss how things used to be between us.",
        
#         "I've asked them politely so many times and they still ignore me.",
#         "Why does nobody ever listen when I explain something?",
#         "I'm seriously irritated by how this situation was handled.",
        
#         "I keep thinking about everything that could go wrong.",
#         "I have an important meeting tomorrow and I can't calm down.",
#         "I don't know what I'm going to do if this doesn't work out.",
        
#         "I've been trying to fix this for hours and I'm getting nowhere.",
#         "Nothing seems to work no matter what I try.",
#         "I'm so fed up with dealing with the same problem again and again.",
        
#         "What time does the train leave tomorrow?",
#         "Can you explain how photosynthesis works?",
#         "Remind me to call my brother this evening."
#     ]

#     for sentence in test_sentences:
#         emotion, confidence = emotion_model.predict(sentence)

#         print(f"\nText: {sentence}")
#         print(f"Emotion: {emotion}")
#         print(f"Confidence: {confidence:.2f}")