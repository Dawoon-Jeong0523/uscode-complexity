"""
Title: US Code HTML Scraper
Description: This script downloads US Code Titles (1–52, 54) from govinfo.gov for each year (1994–2023),
removes unwanted HTML elements, and stores the structured text in both .txt and .pkl formats.

Dependencies:
- requests
- beautifulsoup4
- lxml
- tqdm
- pickle
- re
- os
- time
"""

import os
import pickle
import time
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

# List of title numbers to process (1–52, plus 54)
title_nums = list(range(1, 53)) + [54]
error_list = []

# Iterate through years (1994–2023)
for input_year in tqdm(range(1994, 1995)):
    for key in title_nums[:2]:
        # Construct URL for each title and year
        url = f"https://www.govinfo.gov/content/pkg/USCODE-{input_year}-title{key}/html/USCODE-{input_year}-title{key}.htm"

        try:
            # Send HTTP request
            response = requests.get(url)
            response.raise_for_status()  # Raise error if request fails

            # Decode HTML content and parse with BeautifulSoup
            html_str = response.content.decode('utf-8')
            soup = BeautifulSoup(html_str, 'lxml')

            # Remove <div class="analysis"> elements to exclude table of contents
            for div in soup.find_all("div", class_="analysis"):
                div.extract()

            # Get cleaned HTML as a string
            cleaned_html = str(soup)

            # Identify all HTML tags and their positions
            tags = re.finditer(r"<[^>]+>", cleaned_html)
            tag_positions = [(match.start(), match.end(), match.group()) for match in tags]

            # Extract plain text (without tags)
            modified_text = list(cleaned_html)
            for start, end, tag in reversed(tag_positions):
                modified_text[start:end] = [" "] * len(tag)

            structured_text = "".join(modified_text)

            # Create output directory for the year
            make_dir = f'./Data/US_govinfo/{input_year}'
            os.makedirs(make_dir, exist_ok=True)

            # Save cleaned structured text as .txt
            txt_file_path = f'{make_dir}/TITLE_{key}.txt'
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(structured_text)

            # Delay to respect server load
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {url}: {e}")
            error_list.append((input_year, key))

import pandas as pd

error_list_df = pd.DataFrame(error_list, columns=['Year', 'Title'])
error_list_df.to_csv('./Data/US_govinfo/error_list.csv', index=False)