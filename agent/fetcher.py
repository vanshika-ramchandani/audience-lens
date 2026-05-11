from __future__ import annotations
import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def extract_video_id(url: str) -> str | None:
    """
    Extracts the YouTube video ID from various URL formats.
    Supports:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://youtube.com/shorts/VIDEO_ID
    """
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",       # standard watch URL
        r"youtu\.be/([a-zA-Z0-9_-]{11})",    # short URL
        r"shorts/([a-zA-Z0-9_-]{11})",        # shorts URL
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_comments(video_url: str, max_comments: int = 300) -> list[dict]:
    """
    Fetches top-level comments from a YouTube video.

    Args:
        video_url:    Full YouTube video URL
        max_comments: Maximum number of comments to fetch (default 300)

    Returns:
        List of dicts with keys: 'text', 'likes', 'author'

    Raises:
        ValueError: If URL is invalid or video ID can't be extracted
        HttpError: If YouTube API request fails
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not found in environment variables.")

    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {video_url}")

    youtube = build("youtube", "v3", developerKey=api_key)

    comments = []
    next_page_token = None

    try:
        while len(comments) < max_comments:
            # Each page returns up to 100 comments
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                pageToken=next_page_token,
                textFormat="plainText",
                order="relevance",   # fetch most relevant comments first
            )
            response = request.execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "text":   snippet["textDisplay"],
                    "likes":  snippet["likeCount"],
                    "author": snippet["authorDisplayName"],
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break   # no more pages

    except HttpError as e:
        raise HttpError(f"YouTube API error: {e.reason}", e.resp, e.content)

    return comments