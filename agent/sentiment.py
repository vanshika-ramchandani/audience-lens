import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_comment_sentiment(text: str) -> dict:
    """
    Classifies a single comment as positive or negative using Groq.
    Handles multilingual comments including Hinglish.
    """
    client = get_groq_client()
    prompt = f"""Classify the sentiment of this comment as positive or negative.
            The comment may be in English, Hindi, or Hinglish (mix of both).
            Comment: "{text[:300]}"
            Reply with only one word: positive or negative."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
        temperature=0,
    )
    result = response.choices[0].message.content.strip().lower()
    label = "positive" if "positive" in result else "negative"
    return {"label": label, "score": 1.0}


def analyze_cluster_sentiment(cluster: dict) -> dict:
    comments = cluster["comments"]
    if not comments:
        return {**cluster, "sentiment_breakdown": {}, "dominant_sentiment": "unknown"}

    # Send ALL comments in one API call instead of one per comment
    numbered = "\n".join(f'{i+1}. "{c[:200]}"' for i, c in enumerate(comments))
    
    prompt = f"""Classify the sentiment of each comment as positive or negative.
                Comments may be in English, Hindi, or Hinglish.

                {numbered}

                Reply with only a comma-separated list of labels in order.
                Example: positive,negative,positive,positive
                No explanations, no numbering, just the labels."""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0,
    )
    
    raw = response.choices[0].message.content.strip().lower()
    labels = [l.strip() for l in raw.split(",")]
    
    # Fallback if count mismatch
    while len(labels) < len(comments):
        labels.append("positive")
    
    positive_count = sum(1 for l in labels if "positive" in l)
    total = len(comments)
    
    breakdown = {
        "positive": round(min((positive_count / total) * 100, 100.0), 1),
        "negative": round(max(((total - positive_count) / total) * 100, 0.0), 1),
    }
    
    return {
        **cluster,
        "sentiment_breakdown": breakdown,
        "dominant_sentiment": "positive" if positive_count >= total/2 else "negative",
        "avg_confidence": 1.0,
    }

def analyze_all_clusters(clusters: list) -> list:
    return [analyze_cluster_sentiment(cluster) for cluster in clusters]


def get_overall_sentiment(clusters: list) -> dict:
    if not clusters:
        return {"positive": 0, "negative": 0, "dominant": "unknown"}

    total_comments = sum(c["size"] for c in clusters)
    weighted_positive = sum(
        c["sentiment_breakdown"].get("positive", 0) * c["size"]
        for c in clusters
    )

    overall_positive = round(weighted_positive / total_comments, 1)
    overall_negative = round(100 - overall_positive, 1)

    return {
        "positive": overall_positive,
        "negative": overall_negative,
        "dominant": "positive" if overall_positive >= 50 else "negative",
    }