"""
Title: US Code PDF Fallback Extractor
Description: This script handles failed HTML fetches by downloading the corresponding PDF files
and extracting text using pdfminer. Extracted text is saved as .txt files.

Dependencies:
- requests
- pdfminer.six
- tqdm
- os
- time
- pickle
"""

import pickle
import os
import time
import requests
from tqdm import tqdm
from pdfminer.high_level import extract_text

pdf_error_list = []

# Load error list generated from HTML scraper
with open("error_list.pkl", "rb") as f:
    error_list = pickle.load(f)


for error in tqdm(error_list):
    input_year = error[0]
    key = error[1]
    url = f"https://www.govinfo.gov/content/pkg/USCODE-{input_year}-title{key}/pdf/USCODE-{input_year}-title{key}.pdf"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors

        make_dir = f'./Data/US_govinfo/pdf/{input_year}'
        pdf_file_path = f'{make_dir}/TITLE_{key}.pdf'
        os.makedirs(make_dir, exist_ok=True)

        with open(pdf_file_path, 'wb') as f:
            f.write(response.content)

        time.sleep(2)

        try:
            text = extract_text(pdf_file_path)
            with open(f'./Data/US_govinfo/{input_year}/TITLE_{key}.txt', 'w', encoding='utf-8') as f:
                f.write(text)

        except Exception as e:
            print(f"Failed to extract text from {pdf_file_path}: {e}")
            pdf_error_list.append((input_year, key))

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {url}: {e}")
        pdf_error_list.append((input_year, key))