import re
from collections import Counter


MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 500
PASSAGE_LENGTH = 600
MAX_PASSAGES = 2
STOP_WORDS = {
    "about",
    "after",
    "are",
    "can",
    "does",
    "for",
    "from",
    "how",
    "into",
    "that",
    "the",
    "their",
    "this",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}

_uploaded_documents: dict[str, dict] = {}


def store_pdf(user_id: str, filename: str, pages: list[str]) -> dict:
    passages = []

    for page_number, page_text in enumerate(pages, start=1):
        text = page_text.strip()

        for start in range(0, len(text), PASSAGE_LENGTH):
            passage = text[start : start + PASSAGE_LENGTH].strip()

            if passage:
                passages.append(
                    {
                        "page": page_number,
                        "text": passage,
                    }
                )

    if not passages:
        raise ValueError("This PDF contains no extractable text.")

    _uploaded_documents[user_id] = {
        "filename": filename,
        "passages": passages,
    }

    return {
        "filename": filename,
        "pages": len(pages),
    }


def search_uploaded_pdf(user_id: str, query: str) -> dict:
    document = _uploaded_documents.get(user_id)

    if document is None:
        return {
            "found": False,
            "message": "No PDF has been uploaded for this user yet.",
        }

    search_terms = {
        term
        for term in re.findall(r"\w+", query.lower())
        if len(term) > 2 and term not in STOP_WORDS
    }

    if not search_terms:
        return {
            "found": False,
            "message": "The search question did not contain usable keywords.",
        }

    matches = []

    for passage in document["passages"]:
        passage_terms = Counter(
            re.findall(r"\w+", passage["text"].lower())
        )
        score = sum(passage_terms[term] for term in search_terms)

        if score:
            matches.append((score, passage))

    matches.sort(key=lambda result: result[0], reverse=True)
    selected = [passage for _, passage in matches[:MAX_PASSAGES]]

    if not selected:
        return {
            "found": False,
            "filename": document["filename"],
            "message": "No passages in the uploaded PDF matched that question.",
        }

    return {
        "found": True,
        "filename": document["filename"],
        "passages": selected,
    }
