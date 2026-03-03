import os
import re
import json
import pdfplumber
import pytesseract
import cv2
from PIL import Image

# ================= CONFIG =================

PDF_PATH = r"C:\Users\dhars\Downloads\Project-2\Project-2\Week-1\SampleContract1.pdf"
OUTPUT_DIR = r"C:\Users\dhars\Downloads\Project-2\Project-2\week1_output"

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# =========================================

# Create folders
text_dir = os.path.join(OUTPUT_DIR, "extracted_text")
annotation_dir = os.path.join(OUTPUT_DIR, "annotation_ready")

os.makedirs(text_dir, exist_ok=True)
os.makedirs(annotation_dir, exist_ok=True)

# -------- TEXT QUALITY CHECK --------
def analyze_text_quality(text):
    metrics = {
        "total_words": len(text.split()),
        "has_dates": bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)),
        "has_amounts": bool(re.search(r'(Rs\.?\s?\d+(?:,\d{2,3})*)|\$\s*\d+', text)),
        "has_parties": bool(re.search(r'\b(between|party|parties|hereinafter)\b', text, re.I))
    }

    score = 0
    score += 30 if metrics["has_dates"] else 0
    score += 30 if metrics["has_amounts"] else 0
    score += 20 if metrics["has_parties"] else 0
    score += 20 if metrics["total_words"] > 50 else 0

    metrics["quality_score"] = score
    return metrics

# -------- ANNOTATION READY FORMAT --------
def prepare_for_annotation(text, page_no):
    dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
    amounts = re.findall(r'(Rs\.?\s?\d+(?:,\d{2,3})*)|\$\s*\d+', text)

    return {
        "text": text,
        "meta": {
            "page": page_no,
            "suggested_dates": dates[:5],
            "suggested_amounts": amounts[:5]
        }
    }

# ================= MAIN PIPELINE =================

print("📄 Extracting text from PDF using pdfplumber...")

quality_reports = []
annotation_data = []

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"✅ Total pages found: {len(pdf.pages)}")

    for i, page in enumerate(pdf.pages[:3]):  # first 3 pages
        page_no = i + 1
        print(f"\nProcessing Page {page_no}")

        text = page.extract_text()

        if not text:
            text = ""

        # Save extracted text
        with open(
            os.path.join(text_dir, f"page_{page_no}.txt"),
            "w", encoding="utf-8"
        ) as f:
            f.write(text)

        quality = analyze_text_quality(text)
        quality["page"] = page_no
        quality_reports.append(quality)

        annotation_data.append(
            prepare_for_annotation(text, page_no)
        )

        print(f"📊 Quality Score: {quality['quality_score']}/100")
        print(f"📝 Words extracted: {quality['total_words']}")

# Save annotation-ready file
with open(
    os.path.join(annotation_dir, "annotation_ready.jsonl"),
    "w", encoding="utf-8"
) as f:
    for item in annotation_data:
        f.write(json.dumps(item) + "\n")

# Save quality report
with open(
    os.path.join(OUTPUT_DIR, "quality_report.json"),
    "w", encoding="utf-8"
) as f:
    json.dump(quality_reports, f, indent=2)

print("\n✅ Week 1 Document Parsing Pipeline Complete!") 
print("➡ Text extracted, quality verified, annotation-ready data created")

