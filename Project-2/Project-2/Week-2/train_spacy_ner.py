import spacy
import random
import json
from spacy.training.example import Example

TRAIN_FILE = "data/train_data.json"

# ✅ Load JSON training data
with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    TRAIN_DATA = json.load(f)

# ✅ Create blank model
nlp = spacy.blank("en")

# ✅ Add NER component
ner = nlp.add_pipe("ner")

# ✅ Add entity labels
for text, annotations in TRAIN_DATA:
    for start, end, label in annotations["entities"]:
        ner.add_label(label)

# ✅ Training
optimizer = nlp.begin_training()

print("🚀 Training Started...")

for epoch in range(30):   # More epochs = better learning
    random.shuffle(TRAIN_DATA)
    losses = {}

    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)

        nlp.update([example], drop=0.2, losses=losses)

    print(f"Epoch {epoch+1}/30 Loss: {losses['ner']}")

# ✅ Save trained model
nlp.to_disk("contract_ner_model")

print("\n✅ Model trained and saved in Week-2/contract_ner_model")
