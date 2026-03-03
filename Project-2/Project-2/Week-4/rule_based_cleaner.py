import re
from datetime import datetime


# ✅ Normalize Date → ISO Format
def normalize_date(date_text):
    try:
        if re.match(r"\d{1,2}/\d{1,2}/\d{4}", date_text):
            dt = datetime.strptime(date_text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
    except:
        return date_text

    return date_text


# ✅ Normalize Amount → Integer
def normalize_amount(amount_text):

    amount_text = amount_text.replace(",", "")
    numbers = re.findall(r"\d+", amount_text)

    if numbers:
        return int("".join(numbers))

    return amount_text


# ✅ Main Cleaning Function
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
        cleaned[key] = list(set(cleaned[key]))

    return cleaned
