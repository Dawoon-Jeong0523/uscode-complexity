'''
Description:
- preprocess_ocr_text(): Cleans up noisy OCR text
- calculate_entropy(): Computes entropy and normalized entropy for a list
- calculate_text_properties(): Tokenizes and extracts word-level stats from text
'''

import re
import time
import os
import numpy as np
from nltk.tokenize import word_tokenize

# --- Preprocessing: OCR Cleaning ---
def preprocess_ocr_text(text):
    """
    Preprocess the OCR text by cleaning unwanted patterns, tags, and formatting.

    Steps:
    1. Remove <page> and surrounding content.
    2. Eliminate specific phrases and whitespace inconsistencies.
    3. Normalize text by converting to lowercase and removing extra spaces.

    Args:
        text (str): The raw OCR text.

    Returns:
        str: Cleaned and preprocessed text.
    """

    start_time = time.time()  # Track preprocessing time (useful for debugging or optimization if needed)

    # Step 1: Remove <page> tags and their associated lines/content
    pattern_1 = r"<page>(?:\n.*){2}"  # Matches <page> and the two lines below (e.g., metadata or title content)
    pattern_2 = r".*\n</page>"        # Matches the line above </page> and the closing tag itself

    # Apply substitutions to remove unnecessary page content
    text = re.sub(pattern_1, "\n", text)
    text = re.sub(pattern_2, "\n", text)

    # Step 2: Remove specific tags and unwanted phrases
    text = re.sub('<page>', '', text)  # Remove <page> tags directly if still present
    text = re.sub('</page>', '', text)  # Remove </page> tags directly if still present

    # Remove a known phrase related to incorrect prompts in the OCR process
    text = re.sub(r"Please provide the text you would like me to correct\.  I need the OCR'd text to be able to help you", ' ', text)

    # Step 3: Normalize whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with a single space

    # Step 4: Convert to lowercase for uniformity
    text = text.lower()

    # Final cleanup: Strip leading and trailing spaces
    text = text.strip()

    return text

# --- Entropy Calculation ---
def calculate_entropy(temp_list):
    """
    Calculate entropy and normalized entropy for a given list.

    Parameters:
        temp_list (list): A list of values.

    Returns:
        tuple: (entropy, normalized_entropy)
    """
    # Convert the list to a probability distribution
    values, counts = np.unique(temp_list, return_counts=True)
    probabilities = counts / counts.sum()

    # Calculate Shannon entropy
    entropy = -np.sum(probabilities * np.log2(probabilities))

    # Calculate maximum entropy (log2 of unique values)
    max_entropy = np.log2(len(values))

    # Calculate normalized entropy
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    return entropy, normalized_entropy

import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')

# --- Text Analysis ---
def calculate_text_properties(text):
    """
    Calculate various properties of a given text using NLTK.

    Args:
        text (str): Input text to analyze.

    Returns:
        tuple: (character length, word count, unique word count)
    """
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]

    return text, words, set(words)