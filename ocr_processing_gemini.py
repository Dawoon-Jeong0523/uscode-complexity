"""
This script reads OCR-extracted text from a file, uses Google Gemini (1.5 Flash) to correct typos and spacing, and saves the cleaned result.

Dependencies:
- google-generativeai
- tqdm
- pickle
- os
"""

import google.generativeai as genai
import os
import pickle
from tqdm import tqdm

# Set Gemini API key (best practice: use environment variable or secret manager)
############################################################################################
os.environ["API_KEY"] = "YOUR_API_KEY_HERE"  # 🔐 Replace this securely in real use
genai.configure(api_key=os.environ["API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Load raw OCR text
ocr_file_path = './Data/OCR samples/ocr_sample1.txt'
with open(ocr_file_path, 'r', encoding='utf-8', errors='ignore') as file:
    ocr_text = file.read()

# Create correction prompt
prompt = f"Correct the following string for typos and spacing, making it legible. Return only the corrected string:\n'''{ocr_text}'''"

# Send prompt to Gemini model
response = model.generate_content(prompt)
corrected_text = response.text.strip()

# Save cleaned text
output_path = './Data/OCR_sample_processed/processed.txt'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as txt_file:
    txt_file.write(corrected_text)
