import pandas as pd
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import pickle

# ==========================================
# DATASET PATHS
# ==========================================

RAW_DATASET = Path("ML/data/iris_emotion_dataset_raw.csv")
CLEAN_DATASET = Path("ML/data/iris_emotion_dataset_clean.csv")

TRAIN_DATASET = Path("ML/data/iris_emotion_train.csv")
TEST_DATASET = Path("ML/data/iris_emotion_test.csv")


VALID_EMOTIONS = {
    "happy",
    "sad",
    "angry",
    "anxious",
    "frustrated",
    "neutral"
}


# ==========================================
# DATASET PREPROCESSING
# ==========================================

def preprocess_text(text):
    """Clean text while preserving its original meaning."""

    text = str(text).strip()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Normalize quotation marks
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')

    return text


def preprocess_dataset():

    print("\nLoading raw dataset...")

    if not RAW_DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATASET.resolve()}"
        )

    df = pd.read_csv(RAW_DATASET)

    original_count = len(df)

    print(f"Original records: {original_count}")

    # 1. Validate required columns

    required_columns = {
        "text",
        "emotion",
        "scenario",
        "generation_group",
        "scenario_id"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Remove missing values

    required = [
        "text",
        "emotion",
        "scenario",
        "generation_group",
        "scenario_id"
    ]

    df = df.dropna(subset=required).copy()

    # 3. Clean text

    df["text"] = df["text"].apply(preprocess_text)

    # 4. Normalize emotion labels

    df["emotion"] = (
        df["emotion"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df[df["text"] != ""]
    df = df[df["emotion"].isin(VALID_EMOTIONS)]

    # 5. Remove exact duplicate text-label pairs

    df = df.drop_duplicates(
        subset=["text", "emotion"],
        keep="first"
    )

    # 6. Detect conflicting emotion labels

    conflicts = df.groupby("text")["emotion"].nunique()

    conflicting_texts = conflicts[conflicts > 1]

    if not conflicting_texts.empty:
        raise ValueError(
            f"Found {len(conflicting_texts)} texts "
            "assigned to multiple emotion labels."
        )

    # 7. Preserve column order

    df = df[
        [
            "text",
            "emotion",
            "scenario",
            "generation_group",
            "scenario_id"
        ]
    ]

    df = df.reset_index(drop=True)

    # 8. Save clean dataset

    df.to_csv(CLEAN_DATASET, index=False)

    # 9. Summary

    print("\n========== PREPROCESSING SUMMARY ==========")

    print(f"Original records : {original_count}")
    print(f"Clean records    : {len(df)}")
    print(f"Removed records  : {original_count - len(df)}")

    print("\nEmotion distribution:")
    print(df["emotion"].value_counts().sort_index())

    print("\nUnique scenario IDs:", df["scenario_id"].nunique())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nClean dataset saved:")
    print(CLEAN_DATASET.resolve())

    print("\n============================================")


# ==========================================
# TRAIN-TEST SPLITTING
# ==========================================

def split_dataset():

    print("\nLoading clean dataset for splitting...")

    if not CLEAN_DATASET.exists():
        raise FileNotFoundError(
            "Clean dataset not found. Run preprocessing first."
        )

    df = pd.read_csv(CLEAN_DATASET)

    X = df["text"]
    y = df["emotion"]
    groups = df["generation_group"]

    # 5-fold stratified group splitting

    splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    train_indices, test_indices = next(
        splitter.split(X, y, groups)
    )

    train_df = df.iloc[train_indices].copy()
    test_df = df.iloc[test_indices].copy()

    # Verify group separation

    train_groups = set(train_df["generation_group"])
    test_groups = set(test_df["generation_group"])

    overlap = train_groups.intersection(test_groups)

    if overlap:
        raise ValueError(
            f"Group leakage detected: {len(overlap)} overlapping groups"
        )

    # Save datasets

    train_df.to_csv(TRAIN_DATASET, index=False)
    test_df.to_csv(TEST_DATASET, index=False)

    # Summary

    print("\n========== SPLITTING SUMMARY ==========")

    print(f"Total records : {len(df)}")
    print(f"Training data : {len(train_df)}")
    print(f"Testing data  : {len(test_df)}")

    print("\nTraining emotion distribution:")
    print(train_df["emotion"].value_counts().sort_index())

    print("\nTesting emotion distribution:")
    print(test_df["emotion"].value_counts().sort_index())

    print("\nGeneration groups in training:", len(train_groups))
    print("Generation groups in testing :", len(test_groups))
    print("Overlapping groups            :", len(overlap))

    print("\nTraining dataset saved:", TRAIN_DATASET)
    print("Testing dataset saved :", TEST_DATASET)

    print("\n=======================================")


# ==========================================
# TF-IDF VECTORIZATION
# ==========================================

def vectorize_text():

    print("\nLoading training and testing datasets...")

    if not TRAIN_DATASET.exists() or not TEST_DATASET.exists():
        raise FileNotFoundError(
            "Training or testing dataset missing. "
            "Run split_dataset() first."
        )

    train_df = pd.read_csv(TRAIN_DATASET)
    test_df = pd.read_csv(TEST_DATASET)

    # Validate datasets

    if train_df.empty or test_df.empty:
        raise ValueError("Training or testing dataset is empty.")

    if train_df["text"].isna().any() or test_df["text"].isna().any():
        raise ValueError("Missing text values detected.")

    X_train = train_df["text"]
    X_test = test_df["text"]

    y_train = train_df["emotion"]
    y_test = test_df["emotion"]

    # Initialize TF-IDF

    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )

    # Fit ONLY on training data

    X_train_tfidf = tfidf.fit_transform(X_train)

    # Transform testing data using training vocabulary

    X_test_tfidf = tfidf.transform(X_test)

    # Summary

    print("\n========== TF-IDF SUMMARY ==========")

    print("Training matrix shape:", X_train_tfidf.shape)
    print("Testing matrix shape :", X_test_tfidf.shape)

    print("Vocabulary size      :", len(tfidf.vocabulary_))

    print("Training labels      :", len(y_train))
    print("Testing labels       :", len(y_test))

    print("\nTF-IDF vectorization completed successfully.")

    return (
        X_train_tfidf,
        X_test_tfidf,
        y_train,
        y_test,
        tfidf
    )


# ==========================================
# LOGISTIC REGRESSION MODEL
# ==========================================

def train_logistic_regression():

    print("\nLoading training dataset...")

    train_df = pd.read_csv(TRAIN_DATASET)

    X_train = train_df["text"]
    y_train = train_df["emotion"]
    groups = train_df["generation_group"]

    # TF-IDF + Logistic Regression pipeline

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                sublinear_tf=True
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                random_state=42
            )
        )
    ])

    # Hyperparameter search

    param_grid = {
        "classifier__C": [0.1, 1, 10]
    }

    # Group-aware stratified cross-validation

    cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    print("\nTraining Logistic Regression...")
    print("Testing C values:", param_grid["classifier__C"])

    grid_search.fit(
        X_train,
        y_train,
        groups=groups
    )

    # Best model results

    best_model = grid_search.best_estimator_

    print("\n========== LOGISTIC REGRESSION RESULTS ==========")

    print("Best parameters:", grid_search.best_params_)

    print(
        "Best cross-validation Macro F1:",
        round(grid_search.best_score_, 4)
    )

    print("\nLogistic Regression training completed.")
    print("\n=======================================")

    return best_model



# ==========================================
# Multinomial Naive Bayes
# ==========================================


def train_naive_bayes():

    print("\nLoading training dataset...")

    train_df = pd.read_csv(TRAIN_DATASET)

    X_train = train_df["text"]
    y_train = train_df["emotion"]
    groups = train_df["generation_group"]

    print("\nTraining Multinomial Naive Bayes...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            sublinear_tf=True
        )),
        ("classifier", MultinomialNB())
    ])

    param_grid = {
        "classifier__alpha": [0.01, 0.1, 0.5, 1.0, 2.0, 5.0]
    }

    cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(
        X_train,
        y_train,
        groups=groups
    )

    best_model = grid_search.best_estimator_

    print("\n========== NAIVE BAYES RESULTS ==========")
    print("Best parameters:", grid_search.best_params_)
    print("Best cross-validation Macro F1:", round(grid_search.best_score_, 4))

    print("\nNaive Bayes training completed.")
    print("========================================")

    return best_model

# ==========================================
# Evaluate Models
# ==========================================

def evaluate_models(logistic_model, naive_bayes_model):

    print("\nLoading primary test dataset...")

    test_df = pd.read_csv(TEST_DATASET)

    X_test = test_df["text"]
    y_test = test_df["emotion"]

    models = {
        "Logistic Regression": logistic_model,
        "Multinomial Naive Bayes": naive_bayes_model
    }

    for name, model in models.items():

        print(f"\n========== {name} TEST RESULTS ==========")

        predictions = model.predict(X_test)

        print("Accuracy:",
              round(accuracy_score(y_test, predictions), 4))

        print("Macro Precision:",
              round(precision_score(
                  y_test, predictions, average="macro"
              ), 4))

        print("Macro Recall:",
              round(recall_score(
                  y_test, predictions, average="macro"
              ), 4))

        print("Macro F1:",
              round(f1_score(
                  y_test, predictions, average="macro"
              ), 4))

        print("\nClassification Report:")
        print(classification_report(y_test, predictions))

        print("Confusion Matrix:")
        print(confusion_matrix(
            y_test,
            predictions,
            labels=model.classes_
        ))


# ==========================================
# SAVING THE MODEL
# ==========================================

MODEL_PATH = Path("ML/model/emotion_model.pkl")


def save_model(model):

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    saved_model = {
        "model": model,
        "model_name": "Multinomial Naive Bayes",
        "best_parameters": {
            "classifier__alpha": 0.01
        },
        "cross_validation_macro_f1": 0.9965
    }

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(saved_model, file)

    print(f"\nModel saved successfully: {MODEL_PATH}")

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    # split_dataset()
    # preprocess_dataset()

    logistic_model = train_logistic_regression()
    naive_bayes_model = train_naive_bayes()

    evaluate_models(logistic_model, naive_bayes_model)

    save_model(naive_bayes_model)
