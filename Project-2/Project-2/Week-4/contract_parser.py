import pdfplumber
import re
from rule_based_cleaner import clean_entities


# ✅ Extract Text from PDF
def extract_text_from_pdf(pdf_path):

    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:2]:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    return full_text


# ✅ Main Contract Parsing Function
def parse_contract(pdf_path):

    text = extract_text_from_pdf(pdf_path)

    raw_entities = []

    # ✅ DATE Extraction (dd/mm/yyyy)
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", text)
    for d in dates:
        raw_entities.append((d, "DATE"))

    # ✅ AMOUNT Extraction (Rs, ₹ formats)
    amounts = re.findall(r"Rs\.?\s?\d+(?:,\d{2,3})*|₹\s?\d+(?:,\d{2,3})*", text)
    for a in amounts:
        raw_entities.append((a, "AMOUNT"))

    # ✅ PARTY Extraction (Multiline Between Rule)
    party_match = re.search(
        r"between\s+the\s+(.*?)\s+hereinafter",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if party_match:
        commission_name = " ".join(party_match.group(1).split())
        raw_entities.append((commission_name, "PARTY"))

    # ✅ CONSULTANT Party
    if "CONSULTANT" in text.upper():
        raw_entities.append(("CONSULTANT", "PARTY"))

    # ✅ IIT Kanpur Party (Contract2)
    iit_match = re.search(r"Indian Institute of Technology.*?Kanpur", text, re.I)
    if iit_match:
        raw_entities.append((iit_match.group(0), "PARTY"))

    # ✅ Jurisdiction Extraction
    juris = re.search(r"courts in (\w+)", text, re.I)
    if juris:
        raw_entities.append((juris.group(1), "JURISDICTION"))

    # ✅ Clean Final Output JSON
    final_output = clean_entities(raw_entities)

    return final_output
