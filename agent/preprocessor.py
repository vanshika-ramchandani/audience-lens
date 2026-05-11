import re


def clean_text(text: str) -> str:
    """
    Cleans a single comment string:
    - Removes URLs
    - Removes emojis and non-ASCII characters
    - Strips excess whitespace
    - Lowercases for consistency
    """
    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
    # Remove special characters except basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s.,!?'-]", "", text)
    # Collapse multiple spaces/newlines into one
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def is_valid_comment(text: str, min_words: int = 2) -> bool:
    """
    Filters out low-quality comments:
    - Too short (less than min_words words)
    - Mostly numbers or single characters
    - Empty after cleaning
    """
    if not text:
        return False
    words = text.split()
    if len(words) < min_words:
        return False
    # Reject if more than 80% of words are single characters (e.g. "l o l")
    single_char_words = sum(1 for w in words if len(w) == 1)
    if single_char_words / len(words) > 0.8:
        return False
    return True


def preprocess_comments(raw_comments: list[dict]) -> list[dict]:
    """
    Cleans and filters a list of raw comment dicts.

    Args:
        raw_comments: List of dicts with keys 'text', 'likes', 'author'

    Returns:
        Filtered list of dicts with added 'clean_text' key
    """
    processed = []

    for comment in raw_comments:
        original_text = comment.get("text", "")
        cleaned = clean_text(original_text)

        if not is_valid_comment(cleaned):
            continue  # skip low-quality comments

        processed.append({
            "text":       original_text,   # keep original for display
            "clean_text": cleaned,         # use this for ML/LLM processing
            "likes":      comment.get("likes", 0),
            "author":     comment.get("author", ""),
        })

    print(f"Raw: {len(raw_comments)} → After filtering: {len(processed)}")

    return processed