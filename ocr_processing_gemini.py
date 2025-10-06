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
os.environ["API_KEY"] = "Your API KEY"  # 🔐 Replace this securely in real use
genai.configure(api_key=os.environ["API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Load raw OCR text
ocr_file_path = './Data/OCR samples/ocr_sample1.txt'
with open(ocr_file_path, 'r', encoding='utf-8', errors='ignore') as file:
    ocr_text = file.read()

INSTRUCTION = """
You are an OCR text normalizer.
- Correct the following string for typos and spacing, making it legible. Return only the corrected string
"""

FEW_SHOT = """
### Example
<INPUT>
§ 1. Time for election os Sienators.
§ 2. Number and apportionment of Repicsentatlveg.
§ 3. Election by dlistricts.
§ 4. Additional ltepreientatves at large.
§ 5. Nominations for lteprementatlves at large.
§ 0. ltedcuetion ofrpresenti-tlon.
§ 7. Time of election.
§ 8. Vacancies.
§ 9. Voting for ltepresentatives.
</INPUT>
<OUTPUT>
§ 1. Time for election of Senators
§ 2. Number and apportionment of Representatives.
§ 3. Election by districts.
§ 4. Additional Representatives at large.
§ 5. Nominations for Representatives at large.
§ 6. Reduction of representation.
§ 7. Time of election.
§ 8. Vacancies.
§ 9. Voting for Representatives.
</OUTPUT>
"""

def normalize_ocr_text(ocr_text: str) -> str:
    prompt = f"""{INSTRUCTION}

    {FEW_SHOT}

    Now correct the following OCR text.
    <INPUT>
    {ocr_text}
    </INPUT>
    <OUTPUT>"""
    # 2) Single call (keep your generation_config active)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
        ),
    )
    text = (response.text or "").strip()
    if text.endswith("</OUTPUT>"):
        text = text[:-9].strip()
    # Optional: strip code fences
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    return text

corrected_text = normalize_ocr_text(ocr_text)

# Save cleaned text
output_path = './Data/OCR_sample_processed/processed.txt'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as txt_file:
    txt_file.write(corrected_text)
