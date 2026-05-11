import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def call_groq(prompt: str, max_tokens: int = 500) -> str:
    """
    Sends a prompt to Groq and returns the response text.

    Args:
        prompt:     The prompt to send
        max_tokens: Maximum response length

    Returns:
        LLM response as a string
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.4,   # slightly creative but mostly factual
    )
    return response.choices[0].message.content.strip()


def name_cluster_theme(cluster: dict) -> str:
    """
    Uses LLM to give a human-readable name to a comment cluster.
    Example: "Delivery & Shipping Issues" or "Product Quality Praise"

    Args:
        cluster: Cluster dict with top_comments

    Returns:
        A short theme name (3-6 words)
    """
    sample_comments = "\n".join(f'- "{c}"' for c in cluster["top_comments"][:5])
    dominant = cluster.get("dominant_sentiment", "mixed")

    prompt = f"""
            You are analyzing YouTube comments. Here are some comments from the same group:

            {sample_comments}

            The overall sentiment of this group is: {dominant}

            Give a SHORT theme name (3-6 words) that captures what this group of comments is mainly about.
            Only return the theme name, nothing else. No quotes, no punctuation at the end.
            Example outputs: "Delivery Speed Complaints", "Positive Product Reviews", "Customer Service Issues"
            """
    return call_groq(prompt, max_tokens=20)


def generate_reputation_report(
    clusters: list[dict],
    overall_sentiment: dict,
    video_url: str,
) -> str:
    """
    Generates a full brand reputation report with:
    - What people are saying (themes)
    - Severity assessment
    - Actionable recommendations

    Args:
        clusters:          List of analyzed cluster dicts (with themes + sentiment)
        overall_sentiment: Overall sentiment dict from sentiment.py
        video_url:         The YouTube video URL being analyzed

    Returns:
        Full report as a formatted string
    """
    # Build theme summary for the prompt
    theme_summaries = []
    for c in clusters:
        theme = c.get("theme", f"Theme {c['cluster_id']}")
        sentiment = c.get("dominant_sentiment", "mixed")
        size = c["size"]
        positive_pct = c["sentiment_breakdown"].get("positive", 0)
        sample = c["top_comments"][0] if c["top_comments"] else ""
        theme_summaries.append(
            f'- Theme: "{theme}" | {size} comments | {sentiment} sentiment '
            f'({positive_pct}% positive) | Example: "{sample[:100]}"'
        )

    themes_text = "\n".join(theme_summaries)
    overall_positive = overall_sentiment["positive"]
    overall_negative = overall_sentiment["negative"]

    prompt = f"""
            You are a brand reputation analyst. A YouTube video has been analyzed and its comments grouped into themes.

            Overall sentiment: {overall_positive}% positive, {overall_negative}% negative

            Comment themes:
            {themes_text}

            "Write a brand reputation report with exactly these 3 sections.
            Use plain text headings only, no markdown symbols like # or ##.

            REPUTATION SUMMARY
            (2-3 sentences about overall perception)

            KEY CONCERNS
            (bullet points of main issues)

            RECOMMENDATIONS  
            (bullet points of specific actions)"

            """
    return call_groq(prompt, max_tokens=600)


def label_all_themes(clusters: list[dict]) -> list[dict]:
    """
    Adds a 'theme' label to each cluster using the LLM.

    Args:
        clusters: List of cluster dicts

    Returns:
        Same list with 'theme' key added to each cluster
    """
    labeled = []
    for cluster in clusters:
        theme_name = name_cluster_theme(cluster)
        labeled.append({**cluster, "theme": theme_name})
    return labeled