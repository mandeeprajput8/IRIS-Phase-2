import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

# Load dataset
data = pd.read_csv("data/emotion_dataset.csv")

# Separate input and output
X = data["text"] # what IRIS receives 
y = data["emotion"] # what we want the model to predict [answer]

# 1st step
# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y # [helps preserve approx the same proportion of each emotion is training and testing sets]
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# 2nd step
# Convert text into numerical TF-IDF features
vectorizer = TfidfVectorizer()

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("TF-IDF training shape:", X_train_tfidf.shape)
print("TF-IDF testing shape:", X_test_tfidf.shape)

# 3rd step 
# Create the Logistic Regression model
model = LogisticRegression(max_iter=1000)

# Train the model
model.fit(X_train_tfidf, y_train) # fit() learns from training data

print("Emotion model trained successfully!")

# step 4
# Make predictions on unseen test data
y_pred = model.predict(X_test_tfidf)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)

# Detailed performance report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# step 5
# Save the TF-IDF vectorizer and trained model
with open("model/emotion_model.pkl", "wb") as file:
    pickle.dump(
        {
            "vectorizer": vectorizer,
            "model": model
        },
        file
    )

print("\nEmotion model saved successfully!")