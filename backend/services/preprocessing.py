# ============================================================
# RESQ-FLOW
# MEMBER 3 - TEXT PREPROCESSING
# ============================================================
#
# Purpose:
# Preprocess any user-defined emergency message before it is
# passed to the AI modules.
#
# This module DOES NOT classify the emergency.
# It only cleans and normalizes the input.
#
# ============================================================

import re
import unicodedata


# ------------------------------------------------------------
# 1. UNICODE NORMALIZATION
# ------------------------------------------------------------

def normalize_unicode(text):
    """
    Converts different Unicode representations into
    a consistent form.
    """

    return unicodedata.normalize("NFKC", text)


# ------------------------------------------------------------
# 2. REMOVE URLs
# ------------------------------------------------------------

def remove_urls(text):
    """
    Removes website URLs from the message.
    """

    return re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )


# ------------------------------------------------------------
# 3. REMOVE EMAIL ADDRESSES
# ------------------------------------------------------------

def remove_email_addresses(text):
    """
    Removes email addresses from the message.
    """

    return re.sub(
        r"\S+@\S+\.\S+",
        " ",
        text
    )


# ------------------------------------------------------------
# 4. NORMALIZE WHITESPACE
# ------------------------------------------------------------

def normalize_whitespace(text):
    """
    Converts multiple spaces, tabs and line breaks
    into a single space.
    """

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


# ------------------------------------------------------------
# 5. MAIN PREPROCESSING FUNCTION
# ------------------------------------------------------------

def preprocess_text(message):
    """
    Cleans and normalizes a user-defined emergency message.

    Parameters:
        message (str): Raw message entered by the user.

    Returns:
        str: Preprocessed message.
    """

    if message is None:
        raise ValueError(
            "Emergency message cannot be empty."
        )

    if not isinstance(message, str):
        raise TypeError(
            "Emergency message must be a string."
        )

    # Remove unnecessary spaces at beginning/end
    message = message.strip()

    if not message:
        raise ValueError(
            "Emergency message cannot be empty."
        )

    # Unicode normalization
    message = normalize_unicode(message)

    # Remove URLs
    message = remove_urls(message)

    # Remove email addresses
    message = remove_email_addresses(message)

    # Convert text to lowercase
    message = message.lower()

    # Keep letters, numbers, spaces and basic punctuation.
    # We do NOT remove punctuation such as ! ? . because
    # it can carry useful information for language models.
    message = re.sub(
        r"[^\w\s.,!?'\-]",
        " ",
        message,
        flags=re.UNICODE
    )

    # Remove unnecessary repeated spaces
    message = normalize_whitespace(message)

    return message


# ------------------------------------------------------------
# 6. RETURN ORIGINAL + PROCESSED MESSAGE
# ------------------------------------------------------------

def preprocess_message(message):
    """
    Returns both the original and processed versions
    of the user's message.
    """

    processed_message = preprocess_text(message)

    return {
        "original_message": message,
        "processed_message": processed_message
    }


# ------------------------------------------------------------
# 7. TESTING
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n==========================================")
    print("             RESQ-FLOW")
    print("         TEXT PREPROCESSING")
    print("==========================================")

    print("\nEnter any emergency description.")
    print("Type 'exit' to stop.\n")

    while True:

        message = input("Emergency: ")

        if message.strip().lower() == "exit":

            print("\nPreprocessing stopped.")
            break

        try:

            result = preprocess_message(message)

            print("\nPREPROCESSING RESULT")
            print("----------------------------")

            print(
                "Original message :",
                result["original_message"]
            )

            print(
                "Processed message:",
                result["processed_message"]
            )

            print("----------------------------")

        except (ValueError, TypeError) as error:

            print("\nError:", error)