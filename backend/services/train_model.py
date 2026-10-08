"""
ResQ-Flow AI Model Training

Trains a DistilBERT text classification model for:

1. Disaster type
2. Severity

Input CSV:
    message,disaster_type,severity

The emergency messages come from the dataset.
No emergency messages are hardcoded in this program.
"""

import os
import json
import random

import pandas as pd

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

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "backend",
    "services",
    "emergency_dataset.csv",
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "backend",
    "models",
    "disaster_model"
)

TEST_SIZE = 0.2

RANDOM_STATE = 42


# ============================================================
# LOAD DATASET
# ============================================================

print("\n==============================")
print("RESQ-FLOW AI MODEL TRAINING")
print("==============================")

print("\nLoading dataset...")
print("Dataset:", DATASET_PATH)

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(
    DATASET_PATH
)

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


# ============================================================
# CLEAN DATA
# ============================================================

df = df.dropna(
    subset=required_columns
)

df["message"] = (
    df["message"]
    .astype(str)
    .str.strip()
)

df["disaster_type"] = (
    df["disaster_type"]
    .astype(str)
    .str.strip()
    .str.lower()
)

df["severity"] = (
    df["severity"]
    .astype(str)
    .str.strip()
    .str.lower()
)

df = df[
    df["message"] != ""
]

df = df.drop_duplicates(
    subset=["message"]
)

print(
    f"\nTotal training samples: {len(df)}"
)


# ============================================================
# DISPLAY DATASET CLASSES
# ============================================================

disaster_classes = sorted(
    df["disaster_type"].unique()
)

severity_classes = sorted(
    df["severity"].unique()
)

print("\nDisaster classes:")

for index, label in enumerate(
    disaster_classes
):

    print(
        index,
        "=",
        label
    )


print("\nSeverity classes:")

for index, label in enumerate(
    severity_classes
):

    print(
        index,
        "=",
        label
    )


# ============================================================
# CREATE LABEL MAPPINGS
# ============================================================

disaster_to_id = {
    label: index
    for index, label
    in enumerate(disaster_classes)
}

severity_to_id = {
    label: index
    for index, label
    in enumerate(severity_classes)
}


df["disaster_label"] = df[
    "disaster_type"
].map(
    disaster_to_id
)

df["severity_label"] = df[
    "severity"
].map(
    severity_to_id
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def stratified_split(
    dataframe,
    label_column,
    test_size=0.2,
    random_state=42
):

    random.seed(
        random_state
    )

    train_parts = []
    test_parts = []

    for _, group in dataframe.groupby(
        label_column
    ):

        group = group.sample(
            frac=1,
            random_state=random_state
        )

        if len(group) <= 1:

            train_parts.append(
                group
            )

            continue

        test_count = max(
            1,
            int(
                len(group) * test_size
            )
        )

        test_parts.append(
            group.iloc[
                :test_count
            ]
        )

        train_parts.append(
            group.iloc[
                test_count:
            ]
        )

    train_data = pd.concat(
        train_parts
    ).sample(
        frac=1,
        random_state=random_state
    ).reset_index(
        drop=True
    )

    if test_parts:

        test_data = pd.concat(
            test_parts
        ).sample(
            frac=1,
            random_state=random_state
        ).reset_index(
            drop=True
        )

    else:

        test_data = pd.DataFrame(
            columns=dataframe.columns
        )

    return train_data, test_data


train_df, test_df = stratified_split(
    df,
    "disaster_label",
    TEST_SIZE,
    RANDOM_STATE
)


print(
    "\nTraining samples:",
    len(train_df)
)

print(
    "Testing samples:",
    len(test_df)
)


# ============================================================
# TOKENIZER
# ============================================================

print(
    "\nLoading tokenizer..."
)

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
# CREATE HUGGING FACE DATASETS
# ============================================================

train_dataset = Dataset.from_pandas(
    train_df[
        [
            "message",
            "disaster_label",
        ]
    ],
    preserve_index=False
)

test_dataset = Dataset.from_pandas(
    test_df[
        [
            "message",
            "disaster_label",
        ]
    ],
    preserve_index=False
)


train_dataset = train_dataset.map(
    tokenize,
    batched=True
)

test_dataset = test_dataset.map(
    tokenize,
    batched=True
)


train_dataset = train_dataset.rename_column(
    "disaster_label",
    "labels"
)

test_dataset = test_dataset.rename_column(
    "disaster_label",
    "labels"
)


train_dataset.set_format(
    "torch",
    columns=[
        "input_ids",
        "attention_mask",
        "labels",
    ]
)

test_dataset.set_format(
    "torch",
    columns=[
        "input_ids",
        "attention_mask",
        "labels",
    ]
)


# ============================================================
# LOAD MODEL
# ============================================================

print(
    "\nLoading DistilBERT model..."
)

num_classes = len(
    disaster_classes
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_classes
)


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
)


# ============================================================
# START TRAINING
# ============================================================

print(
    "\n=============================="
)

print(
    "STARTING RESQ-FLOW TRAINING"
)

print(
    "==============================\n"
)


trainer.train()


# ============================================================
# EVALUATION
# ============================================================

print(
    "\n=============================="
)

print(
    "MODEL EVALUATION"
)

print(
    "=============================="
)

results = trainer.evaluate()

print(
    "\nEvaluation results:"
)

for key, value in results.items():

    print(
        key,
        ":",
        value
    )


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

label_mapping = {

    "disaster_labels": {
        str(index): label
        for index, label
        in enumerate(
            disaster_classes
        )
    },

    "severity_labels": {
        str(index): label
        for index, label
        in enumerate(
            severity_classes
        )
    }

}


with open(
    os.path.join(
        OUTPUT_DIR,
        "label_mapping.json"
    ),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        label_mapping,
        file,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print(
    "\n=============================="
)

print(
    "TRAINING COMPLETE"
)

print(
    "=============================="
)

print(
    "\nModel saved to:"
)

print(
    OUTPUT_DIR
)