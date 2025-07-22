# 📘 A Century of Evolution in the Complexity of the United States Legal Code

This repository provides tools and code to reconstruct and analyze the structural evolution of the **U.S. Code** over the past century (1934–2023), with a particular focus on editions before the digital era (pre-1994).

## 🔍 Overview

We leverage **OCR** and **Generative AI** techniques to recover and clean printed historical editions of the Code. This enables computational analysis of federal law even in periods before web-based digital access. The processing pipeline includes:

- 📄 **Contents of U.S. Code**: Word counts, unique word counts, entropy, scaling exponents, etc.
- 🌲 **Hierarchical Structure**: Subtitle → Part → Chapter → Section → Subsection...
- 🔗 **Cross-Reference Relationships**: Title-to-title citation relationships

Due to repository size constraints, this GitHub includes:

- 🔍 A sample OCR text page (`ocr_processing_gemini`) for demonstration
- 🌐 Web-based U.S. Code text from 1994 for structural parsing (`Data Set 2`)

The **full dataset**, including all structured data and graphs for 1934–2023, is hosted on Figshare:  
👉 [Download full dataset (Figshare link)](https://figshare.com/articles/dataset/A_Century_of_Evolution_in_the_Complexity_of_the_United_States_Legal_Code/29540039?file=56173127)

For the complete methodology and validation, please refer to our paper:  
📄 [Read the paper (link)](https://arxiv.org/abs/2507.14342)

## 📁 Repository Structure

```
├── Data/                           # Sample input data and organized folders
│   ├── Data Records/               # Processed datasets for each level (structure, content, citation)
│   ├── OCR samples/                # Example scanned OCR text inputs
│   ├── OCR_sample_processed/       # Cleaned output from OCR preprocessing
│   ├── Technical Validation/       # Datasets used for technical validation
│   ├── US_govinfo/                 # Raw downloaded web-based U.S. Code (1994 sample)
│   ├── Title2Name.csv              # Mapping of Title numbers to their names
│   └── Word_count_df.csv           # Word count data for calculating scaling exponents

├── Figures/                         # Output directory for generated figures

├── contents_functions.py           # Functions for parsing word count and textual statistics
├── parsing_functions.py            # Main parser: extract hierarchical structure from raw text
├── tree_functions.py               # Tree-building, merging, and visualization utilities
├── ocr_processing_gemini.py        # Generative-AI OCR postprocessing pipeline
├── fallback_pdf.py                 # Backup PDF to HTML extraction tool
├── download_html.py                # Web scraper for govinfo HTML content (post-1994)

├── Data_Set1_Figures_part1.py      # Visualizations for Dataset 1 (content-level)
├── Data_Set1_Figures_part2.py
├── Data_Set1_SI_Figures.py         # Supplementary figures
├── Data_Set2_Structure_Parsing.py  # Hierarchical structure parsing (web-based)
├── Data_Set2_Tree_stat.py          # Structural metrics/statistics extraction
├── Data_Set3_Edge_list.py          # Cross-reference edge list construction (citations)

├── Technical_Validation_Figures.py # Reproduction of figures validating against prior studies

├── requirements.txt                # Required Python libraries
└── README.md                       # Project description
```

## 💻 Environment

This project was developed and tested using:

- Python 3.10  
- OS: Windows 10 / Ubuntu 22.04  
- Recommended: Conda virtual environment

To recreate the environment:

```bash
conda create -n uscode-env python=3.10
conda activate uscode-env
pip install -r requirements.txt
```
