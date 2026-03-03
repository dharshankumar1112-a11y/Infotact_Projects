import spacy
import re
from rule_based_cleaner import clean_entities

# ✅ Load trained model
nlp = spacy.load("../Week-2/contract_ner_model")

text = """
This Agreement is made on 12/10/2023 between
SANTA CRUZ COUNTY COMMISSION and ABC Finance Ltd.
Total amount is Rs. 5,00,000 under Chennai jurisdiction.
"""

doc = nlp(text)

# ✅ Model extraction
raw_entities = [(ent.text, ent.label_) for ent in doc.ents]

print("\n✅ RAW ENTITIES FROM MODEL:")
print(raw_entities)

# ✅ Backup if empty
if len(raw_entities) == 0:
    print("\n⚠ Model failed. Using Rule Backup...")

    # DATE
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", text)
    for d in dates:
        raw_entities.append((d, "DATE"))

    # AMOUNT
    amounts = re.findall(r"Rs\.?\s?\d+(?:,\d{2,3})*", text)
    for a in amounts:
        raw_entities.append((a, "AMOUNT"))

    # PARTY (fixed multiline)
    party_match = re.search(
        r"between\s+(.*?)\s+and\s+(.*?)(\.|\n)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if party_match:
        raw_entities.append((party_match.group(1).strip(), "PARTY"))
        raw_entities.append((party_match.group(2).strip(), "PARTY"))

print("\n✅ FINAL RAW ENTITIES:")
print(raw_entities)

# ✅ Cleaning
final_output = clean_entities(raw_entities)

print("\n✅ WEEK-3 FINAL JSON OUTPUT:")
print(final_output)