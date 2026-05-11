import re


def is_valid_youtube_url(url: str) -> bool:
    """
    Checks if a given string is a valid YouTube video URL.
    Supports standard, short, and shorts formats.
    """
    pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[a-zA-Z0-9_-]{11}"
    return bool(re.search(pattern, url))


def format_sentiment_label(dominant: str) -> str:
    """
    Returns an emoji + label string for a sentiment value.
    Used in Streamlit UI for visual clarity.
    """
    mapping = {
        "positive": "🟢 Positive",
        "negative": "🔴 Negative",
        "mixed":    "🟡 Mixed",
        "unknown":  "⚪ Unknown",
    }
    return mapping.get(dominant, "⚪ Unknown")


def truncate_text(text: str, max_chars: int = 200) -> str:
    """
    Truncates a string to max_chars and appends '...' if truncated.
    Used for displaying long comments in the UI without overflow.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def get_severity_level(negative_pct: float) -> tuple[str, str]:
    """
    Classifies reputation severity based on negative comment percentage.

    Returns:
        Tuple of (severity_label, color_hex)
    """
    if negative_pct < 25:
        return ("Healthy", "#22c55e")       # green
    elif negative_pct < 50:
        return ("Needs Attention", "#f59e0b")  # amber
    else:
        return ("Critical", "#ef4444")      # red


def build_summary_stats(clusters: list[dict], overall_sentiment: dict) -> dict:
    """
    Builds a summary stats dict for display in the Streamlit dashboard.

    Returns:
        Dict with total_comments, n_themes, overall_positive, overall_negative, severity
    """
    total_comments = sum(c["size"] for c in clusters)
    n_themes = len(clusters)
    severity_label, severity_color = get_severity_level(overall_sentiment["negative"])

    return {
        "total_comments":   total_comments,
        "n_themes":         n_themes,
        "overall_positive": overall_sentiment["positive"],
        "overall_negative": overall_sentiment["negative"],
        "severity_label":   severity_label,
        "severity_color":   severity_color,
    }