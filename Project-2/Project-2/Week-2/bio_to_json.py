import json

INPUT_FILE = "data/annotated/contract.conll"
OUTPUT_FILE = "data/train_data.json"


def read_conll(filepath):
    sentences = []
    sentence = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line == "":
                if sentence:
                    sentences.append(sentence)
                    sentence = []
            else:
                parts = line.split()
                if len(parts) == 2:
                    token, label = parts
                    sentence.append((token, label))

    return sentences


def conll_to_spacy(sentences):
    training_data = []

    for sent in sentences:
        text = " ".join([w for w, t in sent])

        entities = []
        start = 0
        ent_start = None
        ent_label = None

        for word, tag in sent:
            end = start + len(word)

            # ✅ Begin Entity
            if tag.startswith("B-"):
                if ent_start is not None:
                    entities.append((ent_start, start - 1, ent_label))

                ent_start = start
                ent_label = tag[2:]

            # ✅ Inside Entity
            elif tag.startswith("I-"):
                pass

            # ✅ Outside Entity
            else:
                if ent_start is not None:
                    entities.append((ent_start, start - 1, ent_label))
                    ent_start = None
                    ent_label = None

            start = end + 1

        # Close last entity
        if ent_start is not None:
            entities.append((ent_start, end, ent_label))

        training_data.append((text, {"entities": entities}))

    return training_data


if __name__ == "__main__":
    sentences = read_conll(INPUT_FILE)
    train_data = conll_to_spacy(sentences)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=4)

    print("✅ train_data.json created successfully with full entity spans!")
