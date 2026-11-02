
import pandas as pd
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# FILE PATHS
# ==========================================

DATASET_PATH = Path("ML/data/iris_emotion_dataset_external_test.csv")

TRAIN_DATASET = Path("ML/data/iris_emotion_train.csv")


# ==========================================
# EXTERNAL MODEL EVALUATION
# ==========================================

def evaluate_external_models(logistic_model, naive_bayes_model):

    print("\nLoading external validation dataset...")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"External dataset not found: {DATASET_PATH.resolve()}"
        )

    external_df = pd.read_csv(DATASET_PATH)

    required_columns = {"text", "emotion"}

    if not required_columns.issubset(external_df.columns):
        raise ValueError("External dataset is missing required columns.")

    if external_df.empty or external_df.isnull().any().any():
        raise ValueError("External dataset is empty or contains missing values.")

    X_external = external_df["text"]
    y_external = external_df["emotion"]

    models = {
        "Logistic Regression": logistic_model,
        "Multinomial Naive Bayes": naive_bayes_model
    }

    results = {}

    print(f"\nExternal samples: {len(external_df)}")

    print("\nClass distribution:")
    print(y_external.value_counts().sort_index())

    # --------------------------------------
    # Evaluate each model
    # --------------------------------------

    for model_name, model in models.items():

        print(f"\n{'=' * 15} {model_name} {'=' * 15}")

        predictions = model.predict(X_external)

        accuracy = accuracy_score(y_external, predictions)

        precision = precision_score(
            y_external,
            predictions,
            average="macro",
            zero_division=0
        )

        recall = recall_score(
            y_external,
            predictions,
            average="macro",
            zero_division=0
        )

        f1 = f1_score(
            y_external,
            predictions,
            average="macro",
            zero_division=0
        )

        results[model_name] = {
            "Accuracy": accuracy,
            "Macro Precision": precision,
            "Macro Recall": recall,
            "Macro F1": f1
        }

        print("\nClassification Report:")
        print(
            classification_report(
                y_external,
                predictions,
                zero_division=0
            )
        )

        print("Confusion Matrix:")
        print(
            confusion_matrix(
                y_external,
                predictions,
                labels=sorted(y_external.unique())
            )
        )

    # --------------------------------------
    # Final comparison
    # --------------------------------------

    results_df = pd.DataFrame(results).T

    print("\n========== EXTERNAL EVALUATION COMPARISON ==========")

    print((results_df * 100).round(2).astype(str) + "%")

    print("\n===================================================")

    return results_df


# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":

    from train_emotion_model import (
        train_logistic_regression,
        train_naive_bayes
    )

    print("\nTraining both models...")

    logistic_model = train_logistic_regression()
    naive_bayes_model = train_naive_bayes()

    evaluate_external_models(
        logistic_model,
        naive_bayes_model
    )
