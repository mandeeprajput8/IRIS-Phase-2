import pickle
from pathlib import Path


class EmotionModel:

    def __init__(self):

        model_path = Path(__file__).parent / "emotion_model.pkl"

        with open(model_path, "rb") as file:
            saved_model = pickle.load(file)

        self.model = saved_model["model"]

        print("IRIS Emotion Model loaded successfully.")

    def predict(self, text):

        prediction = self.model.predict([text])[0]

        probabilities = self.model.predict_proba([text])[0]

        confidence = float(max(probabilities))

        return prediction, confidence

# inference testing
from ML.model.emotion_model import EmotionModel

emotion_model = EmotionModel()

tests = [
    "I am extremely happy today!",
    "I feel really sad and lonely.",
    "I am getting frustrated with this situation.",
    "I am feeling anxious about tomorrow.",
    "I am so angry right now.",
    "Everything is normal."
]

for text in tests:

    emotion, confidence = emotion_model.predict(text)

    print(f"\nInput: {text}")
    print(f"Emotion: {emotion}")
    print(f"Confidence: {confidence:.4f}")