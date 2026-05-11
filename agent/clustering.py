import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from collections import defaultdict


# Load model once at module level (avoids reloading on every call)
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def embed_comments(comments: list[str]) -> np.ndarray:
    """
    Converts comment texts into semantic embeddings.

    Args:
        comments: List of cleaned comment strings

    Returns:
        Numpy array of shape (n_comments, embedding_dim)
    """
    embeddings = EMBEDDING_MODEL.encode(comments, show_progress_bar=False)
    # Normalize so cosine similarity = dot product (better for clustering)
    return normalize(embeddings)


def get_optimal_clusters(n_comments: int) -> int:
    """
    Decides number of clusters based on comment volume.
    More comments = more themes, but capped at 6 to keep output readable.
    """
    if n_comments < 30:
        return 3
    elif n_comments < 100:
        return 4
    elif n_comments < 200:
        return 5
    else:
        return 6


def cluster_comments(processed_comments: list[dict]) -> list[dict]:
    """
    Groups comments into thematic clusters.

    Args:
        processed_comments: List of dicts with 'clean_text' and 'text' keys

    Returns:
        List of cluster dicts, each with:
            - 'cluster_id': int
            - 'comments': list of original comment texts in this cluster
            - 'size': number of comments in cluster
            - 'top_comments': top 5 most-liked comments in cluster
    """
    if not processed_comments:
        return []

    clean_texts = [c["clean_text"] for c in processed_comments]
    n_clusters = get_optimal_clusters(len(clean_texts))

    # Generate embeddings
    embeddings = embed_comments(clean_texts)

    # KMeans clustering
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto",
    )
    labels = kmeans.fit_predict(embeddings)

    # Group comments by cluster
    cluster_map = defaultdict(list)
    for idx, label in enumerate(labels):
        cluster_map[label].append(processed_comments[idx])

    # Build output structure
    clusters = []
    for cluster_id, members in cluster_map.items():
        # Sort by likes to surface most resonant comments
        sorted_members = sorted(members, key=lambda x: x["likes"], reverse=True)
        clusters.append({
            "cluster_id":   cluster_id,
            "comments":     [m["text"] for m in members],
            "size":         len(members),
            "top_comments": [m["text"] for m in sorted_members[:5]],
        })

    # Sort clusters by size (largest theme first)
    clusters.sort(key=lambda x: x["size"], reverse=True)

    return clusters