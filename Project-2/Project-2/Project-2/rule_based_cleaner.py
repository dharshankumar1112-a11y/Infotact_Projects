import re
from datetime import datetime

# ✅ Fix Date into Proper Format
def normalize_date(date_text):

    # Example: 12/10/2023 → 2023-10-12
    try:
        if re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_text):
            dt = datetime.strptime(date_text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
    except:
        return date_text

    return date_text


# ✅ Fix Money Amount
def normalize_amount(amount_text):

    # Example: Rs. 5,00,000 → 500000
    amount_text = amount_text.replace(",", "")
    numbers = re.findall(r"\d+", amount_text)

    if numbers:
        return int("".join(numbers))

    return amount_text


# ✅ Remove Duplicate Items
def remove_duplicates(items):
    return list(set(items))


# ✅ Main Cleaner Function
def clean_entities(raw_entities):

    cleaned = {
        "PARTY": [],
        "DATE": [],
        "AMOUNT": [],
        "JURISDICTION": []
    }

    for text, label in raw_entities:

        if label == "DATE":
            cleaned["DATE"].append(normalize_date(text))

        elif label == "AMOUNT":
            cleaned["AMOUNT"].append(normalize_amount(text))

        elif label == "PARTY":
            cleaned["PARTY"].append(text.strip())

        elif label == "JURISDICTION":
            cleaned["JURISDICTION"].append(text.strip())

    # Remove duplicates
    for key in cleaned:
        cleaned[key] = remove_duplicates(cleaned[key])

    return cleaned
