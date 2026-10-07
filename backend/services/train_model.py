"""
ResQ-Flow AI Model Training

Trains a text classification model for:
1. Disaster type
2. Severity

Input CSV:
    message,disaster_type,severity

Example:
    "Water has entered my house",flood,high
"""

import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)

from datasets import Dataset


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "distilbert-base-uncased"

DATASET_PATH = "backend/data/emergency_dataset.csv"

OUTPUT_DIR = "backend/models/disaster_model"

TEST_SIZE = 0.2

RANDOM_STATE = 42


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

required_columns = [
    "message",
    "disaster_type",
    "severity",
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing column in dataset: {column}"
        )

# Remove empty rows
df = df.dropna(
    subset=required_columns
)

# Remove duplicate messages
df = df.drop_duplicates(
    subset=["message"]
)

print(f"Total training samples: {len(df)}")


# ============================================================
# ENCODE DISASTER TYPES
# ============================================================

disaster_encoder = LabelEncoder()

df["disaster_label"] = disaster_encoder.fit_transform(
    df["disaster_type"]
)

print("\nDisaster classes:")

for index, label in enumerate(
    disaster_encoder.classes_
):
    print(index, "=", label)


# ============================================================
# ENCODE SEVERITY
# ============================================================

severity_encoder = LabelEncoder()

df["severity_label"] = severity_encoder.fit_transform(
    df["severity"]
)

print("\nSeverity classes:")

for index, label in enumerate(
    severity_encoder.classes_
):
    print(index, "=", label)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

train_df, test_df = train_test_split(
    df,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=df["disaster_label"],
)

print("\nTraining samples:", len(train_df))
print("Testing samples:", len(test_df))


# ============================================================
# TOKENIZER
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


def tokenize(batch):

    return tokenizer(
        batch["message"],
        padding="max_length",
        truncation=True,
        max_length=128,
    )


# ============================================================
# CREATE DATASETS
# ============================================================

train_dataset = Dataset.from_pandas(
    train_df[
        [
            "message",
            "disaster_label",
        ]
    ]
)

test_dataset = Dataset.from_pandas(
    test_df[
        [
            "message",
            "disaster_label",
        ]
    ]
)


train_dataset = train_dataset.map(
    tokenize,
    batched=True,
)

test_dataset = test_dataset.map(
    tokenize,
    batched=True,
)


train_dataset = train_dataset.rename_column(
    "disaster_label",
    "labels",
)

test_dataset = test_dataset.rename_column(
    "disaster_label",
    "labels",
)


train_dataset.set_format(
    "torch",
    columns=[
        "input_ids",
        "attention_mask",
        "labels",
    ],
)

test_dataset.set_format(
    "torch",
    columns=[
        "input_ids",
        "attention_mask",
        "labels",
    ],
)


# ============================================================
# MODEL
# ============================================================

print("\nLoading model...")

num_classes = len(
    disaster_encoder.classes_
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_classes,
)


# ============================================================
# TRAINING METRICS
# ============================================================

def compute_metrics(eval_prediction):

    predictions, labels = eval_prediction

    predictions = predictions.argmax(
        axis=-1
    )

    accuracy = accuracy_score(
        labels,
        predictions,
    )

    return {
        "accuracy": accuracy
    }


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

training_args = TrainingArguments(

    output_dir=OUTPUT_DIR,

    num_train_epochs=3,

    per_device_train_batch_size=8,

    per_device_eval_batch_size=8,

    learning_rate=2e-5,

    weight_decay=0.01,

    logging_steps=10,

    eval_strategy="epoch",

    save_strategy="epoch",

    load_best_model_at_end=True,

    report_to="none",
)


# ============================================================
# TRAINER
# ============================================================

trainer = Trainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=test_dataset,

    compute_metrics=compute_metrics,
)


# ============================================================
# START TRAINING
# ============================================================

print("\n==============================")
print("STARTING RESQ-FLOW TRAINING")
print("==============================\n")

trainer.train()


# ============================================================
# EVALUATION
# ============================================================

print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

results = trainer.evaluate()

print(results)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

trainer.save_model(
    OUTPUT_DIR
)

tokenizer.save_pretrained(
    OUTPUT_DIR
)


# ============================================================
# SAVE LABEL MAPPINGS
# ============================================================

import json


label_mapping = {

    "disaster_labels": {
        str(index): label
        for index, label
        in enumerate(
            disaster_encoder.classes_
        )
    },

    "severity_labels": {
        str(index): label
        for index, label
        in enumerate(
            severity_encoder.classes_
        )
    }
}


with open(
    os.path.join(
        OUTPUT_DIR,
        "label_mapping.json"
    ),
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        label_mapping,
        file,
        indent=4,
    )


print("\n==============================")
print("TRAINING COMPLETE")
print("==============================")

print(
    f"\nModel saved to: {OUTPUT_DIR}"
)