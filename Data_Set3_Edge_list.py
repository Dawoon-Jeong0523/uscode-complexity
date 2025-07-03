import contents_functions as cf
import re
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd
from tqdm import tqdm

year = 1994
edge_list = []

for i in tqdm(range(1,2)):
    with open(f'./Data/US_govinfo/{year}/TITLE_{i}.txt', 'r', encoding='utf-8') as f:
        title_i = f.read()
    cleaned_title_i = cf.preprocess_ocr_text(title_i)
    
    # Regex to match 'title X' pattern
    pattern = r"title\s+\d{1,2}"

    # Sentence tokenization
    sentences = sent_tokenize(title_i)

    # Extract sentences containing the pattern
    sentences_with_matches = [s.strip() for s in sentences if re.search(pattern, s)]

    for j in tqdm(range(1,51)):
        if i == j:
            continue
        with open(f'./Data/US_govinfo/{year}/TITLE_{j}.txt', 'r', encoding='utf-8') as f:
            title_j = f.read()
        cleaned_title_j = cf.preprocess_ocr_text(title_i)
        temp_list = []

        for sentence in sentences_with_matches:
            matches = re.findall(pattern, sentence)
            temp_weight = len([x for x in matches if x == f'title {j}'])
            if temp_weight >= 1:
                temp_list.append(sentence)
                # Append to edge list
                edge_list.append({
                    'Citing': i,
                    'Cited': j,
                    'Year': year,
                    'Weight': temp_weight,
                    'Citing_text': sentence
                })

edge_df = pd.DataFrame(edge_list)
edge_df.to_csv(f'./Data/Data Records/Data Set3/test_edge_list_web.csv', index=False)