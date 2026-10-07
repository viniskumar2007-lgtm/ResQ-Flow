"""
ResQ-Flow Model Evaluation

Evaluates the trained disaster classification model.

Metrics:
    - Accuracy
    - Precision
    - Recall
    - F1 Score
    - Confusion Matrix
    - Classification Report

Dataset:
    backend/data/emergency_dataset.csv

Trained model:
    backend/models/disaster_model/
"""

import os
import json

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

import torch


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = "backend/models/disaster_model"

DATASET_PATH = "backend/data/emergency_dataset.csv"

TEST_SIZE = 0.20

RANDOM_STATE = 42


# ============================================================
# LOAD LABEL MAPPING
# ============================================================

mapping_path = os.path.join(
    MODEL_PATH,
    "label_mapping.json"
)

if not os.path.exists(mapping_path):

    raise FileNotFoundError(
        "label_mapping.json not found.\n"
        "Train the model first using train_model.py."
    )


with open(
    mapping_path,
    "r",
    encoding="utf-8"
) as file:

    label_mapping = json.load(file)


disaster_labels = label_mapping[
    "disaster_labels"
]

# Convert:
# {"0": "earthquake", "1": "fire"}
#
# into:
# ["earthquake", "fire"]

label_names = [
    disaster_labels[str(i)]
    for i in range(len(disaster_labels))
]


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(
    DATASET_PATH
)

df = df.dropna(
    subset=[
        "message",
        "disaster_type",
    ]
)

df = df.drop_duplicates(
    subset=["message"]
)


# ============================================================
# CREATE LABELS
# ============================================================

# Use the SAME mapping created during training.

label_to_id = {
    label: int(index)
    for index, label in disaster_labels.items()
}


df["label"] = df[
    "disaster_type"
].map(label_to_id)


# Remove unknown labels
df = df.dropna(
    subset=["label"]
)

df["label"] = df[
    "label"
].astype(int)


# ============================================================
# CREATE SAME TEST SPLIT
# ============================================================

_, test_df = train_test_split(

    df,

    test_size=TEST_SIZE,

    random_state=RANDOM_STATE,

    stratify=df["label"],
)


print(
    f"Total test samples: {len(test_df)}"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading trained model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()


# ============================================================
# SELECT DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

model.to(device)

print(
    f"Using device: {device}"
)


# ============================================================
# PREDICTION
# ============================================================

predictions = []

actual_labels = []


print("\nRunning predictions...")

for _, row in test_df.iterrows():

    message = str(
        row["message"]
    )

    actual = int(
        row["label"]
    )

    inputs = tokenizer(

        message,

        return_tensors="pt",

        truncation=True,

        padding=True,

        max_length=128,
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(
            **inputs
        )

    predicted = torch.argmax(
        outputs.logits,
        dim=1
    ).item()

    predictions.append(
        predicted
    )

    actual_labels.append(
        actual
    )


# ============================================================
# ACCURACY
# ============================================================

accuracy = accuracy_score(
    actual_labels,
    predictions
)


print("\n================================")
print("RESQ-FLOW MODEL EVALUATION")
print("================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


# ============================================================
# PRECISION / RECALL / F1
# ============================================================

precision, recall, f1, _ = (
    precision_recall_fscore_support(

        actual_labels,

        predictions,

        average="weighted",

        zero_division=0,
    )
)


print(
    f"Precision: {precision * 100:.2f}%"
)

print(
    f"Recall:    {recall * 100:.2f}%"
)

print(
    f"F1 Score:  {f1 * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n================================")
print("CLASSIFICATION REPORT")
print("================================\n")


print(
    classification_report(

        actual_labels,

        predictions,

        labels=list(
            range(len(label_names))
        ),

        target_names=label_names,

        zero_division=0,
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n================================")
print("CONFUSION MATRIX")
print("================================\n")


matrix = confusion_matrix(

    actual_labels,

    predictions,

    labels=list(
        range(len(label_names))
    ),
)


print(
    "Rows = Actual"
)

print(
    "Columns = Predicted\n"
)


print(
    pd.DataFrame(

        matrix,

        index=label_names,

        columns=label_names,
    )
)


# ============================================================
# SHOW WRONG PREDICTIONS
# ============================================================

print("\n================================")
print("EXAMPLE WRONG PREDICTIONS")
print("================================\n")


wrong_count = 0


for index in range(
    len(test_df)
):

    if (
        actual_labels[index]
        != predictions[index]
    ):

        message = test_df.iloc[
            index
        ]["message"]

        actual = label_names[
            actual_labels[index]
        ]

        predicted = label_names[
            predictions[index]
        ]

        print(
            f"Message: {message}"
        )

        print(
            f"Actual: {actual}"
        )

        print(
            f"Predicted: {predicted}"
        )

        print("-" * 50)

        wrong_count += 1

        if wrong_count >= 10:
            break


# ============================================================
# FINAL RESULT
# ============================================================

print("\n================================")
print("EVALUATION COMPLETE")
print("================================")

print(
    f"Test samples: {len(test_df)}"
)

print(
    f"Correct predictions: "
    f"{sum(a == p for a, p in zip(actual_labels, predictions))}"
)

print(
    f"Wrong predictions: "
    f"{sum(a != p for a, p in zip(actual_labels, predictions))}"
)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)