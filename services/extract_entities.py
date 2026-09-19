"""
extract_entities.py
--------------------
Drop-in helper for Module 2 (PDF Review). Takes raw extracted text from
an uploaded contract (e.g. from PyMuPDF) and returns grouped entity
spans (parties, dates, governing law, renewal terms) using the trained
CRF tagger -- no pretrained model involved.

Usage in your app:
    from extract_entities import extract_entities
    entities = extract_entities(pdf_text, crf_tagger)
    # entities -> [{"text": "Electric City Corp.", "type": "Parties"}, ...]
"""
import re

# Must match the tokenizer used in prepare_crf_data.py / train_crf.py
TOKEN_RE = re.compile(r"\w+(?:[.\-']\w+)*|[^\w\s]")


def word_shape(word):
    shape = []
    for ch in word:
        if ch.isupper():
            shape.append("X")
        elif ch.islower():
            shape.append("x")
        elif ch.isdigit():
            shape.append("d")
        else:
            shape.append(ch)
    collapsed = []
    for ch in shape:
        if not collapsed or collapsed[-1] != ch:
            collapsed.append(ch)
    return "".join(collapsed)


def token_features(tokens, i):
    word = tokens[i]
    features = {
        "bias": 1.0,
        "word.lower": word.lower(),
        "word.isupper": word.isupper(),
        "word.istitle": word.istitle(),
        "word.isdigit": word.isdigit(),
        "word.shape": word_shape(word),
        "word.prefix3": word[:3],
        "word.suffix3": word[-3:],
        "word.length": len(word),
        "position": i,
        "is_first": i == 0,
        "is_last": i == len(tokens) - 1,
    }
    if i > 0:
        prev = tokens[i - 1]
        features.update({
            "-1:word.lower": prev.lower(),
            "-1:word.istitle": prev.istitle(),
            "-1:word.isdigit": prev.isdigit(),
        })
    if i > 1:
        features.update({"-2:word.lower": tokens[i - 2].lower()})
    if i < len(tokens) - 1:
        nxt = tokens[i + 1]
        features.update({
            "+1:word.lower": nxt.lower(),
            "+1:word.istitle": nxt.istitle(),
            "+1:word.isdigit": nxt.isdigit(),
        })
    if i < len(tokens) - 2:
        features.update({"+2:word.lower": tokens[i + 2].lower()})
    return features


def sequence_to_features(tokens):
    return [token_features(tokens, i) for i in range(len(tokens))]


def group_bio_spans(tokens, tags):
    """Turn a list of per-token B-/I-/O tags into grouped entity spans."""
    spans = []
    current_tokens, current_type = [], None
    for token, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if current_tokens:
                spans.append({"text": " ".join(current_tokens), "type": current_type})
            current_tokens = [token]
            current_type = tag[2:]
        elif tag.startswith("I-") and current_type == tag[2:]:
            current_tokens.append(token)
        else:
            if current_tokens:
                spans.append({"text": " ".join(current_tokens), "type": current_type})
            current_tokens, current_type = [], None
    if current_tokens:
        spans.append({"text": " ".join(current_tokens), "type": current_type})
    return spans


def chunk_for_crf(text, max_chars=500):
    """Split long document text into CRF-sized chunks (same scale as
    training data), on paragraph/sentence boundaries where possible."""
    paras = re.split(r"\n\s*\n", text)
    chunks = []
    for para in paras:
        for i in range(0, len(para), max_chars):
            piece = para[i:i + max_chars].strip()
            if piece:
                chunks.append(piece)
    return chunks


def extract_entities(document_text, crf_model):
    """Run the trained CRF tagger over a full document's text and return
    all extracted entity spans, deduplicated by (text, type)."""
    all_spans = []
    for chunk in chunk_for_crf(document_text):
        tokens = [m.group() for m in TOKEN_RE.finditer(chunk)]
        if len(tokens) < 3:
            continue
        features = sequence_to_features(tokens)
        predicted_tags = crf_model.predict([features])[0]
        all_spans.extend(group_bio_spans(tokens, predicted_tags))

    seen = set()
    deduped = []
    for span in all_spans:
        key = (span["text"].lower(), span["type"])
        if key not in seen:
            seen.add(key)
            deduped.append(span)
    return deduped


if __name__ == "__main__":
    import joblib
    from pathlib import Path

    model_path = Path(__file__).resolve().parent.parent / "models" / "crf_tagger.joblib"
    crf = joblib.load(model_path)

    sample_text = (
        "THIS DISTRIBUTOR AGREEMENT (the \"Agreement\") is made by and between "
        "Electric City Corp., a Delaware corporation (\"Company\") and Electric "
        "City of Illinois LLC (\"Distributor\") this 7th day of September, 1999. "
        "This Agreement shall be governed by the laws of the State of New York."
    )
    for span in extract_entities(sample_text, crf):
        print(f"[{span['type']}] {span['text']}")
