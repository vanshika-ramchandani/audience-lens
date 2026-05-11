import streamlit as st
from dotenv import load_dotenv

from agent.fetcher import fetch_comments
from agent.preprocessor import preprocess_comments
from agent.clustering import cluster_comments
from agent.sentiment import analyze_all_clusters, get_overall_sentiment
from agent.summarizer import label_all_themes, generate_reputation_report
from utils.helpers import (
    is_valid_youtube_url,
    format_sentiment_label,
    truncate_text,
    build_summary_stats,
)

# Load environment variables from .env
load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Audience Lens",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #313244;
    }
    .theme-card {
        background: #181825;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #89b4fa;
    }
    .comment-pill {
        background: #313244;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        font-size: 0.85rem;
        color: #cdd6f4;
    }
    .report-box {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #45475a;
        white-space: pre-wrap;
        font-size: 0.95rem;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🔍 Audience Lens")
st.markdown("Paste a YouTube video URL to analyze what the audience is saying about the brand.")
st.divider()

# ── Input ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    video_url = st.text_input(
        label="YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )
with col2:
    max_comments = st.selectbox(
        "Comments to analyze",
        options=[100, 200, 300, 500],
        index=1,
    )

col_btn, col_empty = st.columns([1, 2])
with col_btn:
    analyze_btn = st.button("🚀 Analyze Reputation", type="primary")

# ── Analysis Pipeline ──────────────────────────────────────────────────────────
if analyze_btn:

    # Input validation
    if not video_url:
        st.warning("Please enter a YouTube URL.")
        st.stop()

    if not is_valid_youtube_url(video_url):
        st.error("Invalid YouTube URL. Please check and try again.")
        st.stop()

    # Run pipeline with progress updates
    with st.status("Running analysis...", expanded=True) as status:

        st.write("📥 Fetching comments from YouTube...")
        try:
            raw_comments = fetch_comments(video_url, max_comments=max_comments)
        except Exception as e:
            st.error(f"Failed to fetch comments: {e}")
            st.stop()
        st.write(f"✅ Fetched {len(raw_comments)} comments")

        st.write("🧹 Cleaning and filtering comments...")
        processed = preprocess_comments(raw_comments)
        st.write(f"✅ {len(processed)} valid comments after filtering")

        if len(processed) < 10:
            st.error("Not enough valid comments to analyze. Try a video with more engagement.")
            st.stop()

        st.write("🔗 Grouping comments into themes...")
        clusters = cluster_comments(processed)
        st.write(f"✅ Found {len(clusters)} themes")

        st.write("💬 Analyzing sentiment per theme...")
        clusters = analyze_all_clusters(clusters)
        overall_sentiment = get_overall_sentiment(clusters)

        st.write("🏷️ Labeling themes with AI...")
        clusters = label_all_themes(clusters)

        st.write("📝 Generating reputation report...")
        report = generate_reputation_report(clusters, overall_sentiment, video_url)

        status.update(label="✅ Analysis complete!", state="complete")

    st.divider()

    # ── Summary Metrics ────────────────────────────────────────────────────────
    stats = build_summary_stats(clusters, overall_sentiment)

    st.subheader("📊 Overview")
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Comments Analyzed", stats["total_comments"])
    with m2:
        st.metric("Themes Found", stats["n_themes"])
    with m3:
        st.metric("Positive Sentiment", f"{stats['overall_positive']}%")
    with m4:
        st.metric(
            "Reputation Health",
            stats["severity_label"],
            delta=f"{stats['overall_negative']}% negative",
            delta_color="inverse",
        )

    st.divider()

    # ── Theme Breakdown ────────────────────────────────────────────────────────
    st.subheader("🗂️ Comment Themes")
    st.caption("Each card represents a group of comments talking about the same topic.")

    for cluster in clusters:
        theme     = cluster.get("theme", f"Theme {cluster['cluster_id']}")
        sentiment = format_sentiment_label(cluster.get("dominant_sentiment", "unknown"))
        positive  = cluster["sentiment_breakdown"].get("positive", 0)
        negative  = cluster["sentiment_breakdown"].get("negative", 0)
        size      = cluster["size"]

        with st.expander(f"**{theme}** — {sentiment} ({size} comments)"):
            # Sentiment bar
            col_a, col_b = st.columns(2)
            with col_a:
                st.progress(max(0.0, min(positive / 100, 1.0)), text=f"🟢 Positive: {positive}%")
            with col_b:
                st.progress(max(0.0, min(negative / 100, 1.0)), text=f"🔴 Negative: {negative}%")

            st.markdown("**Top comments in this theme:**")
            for comment in cluster["top_comments"]:
                st.markdown(
                    f'<div class="comment-pill">{truncate_text(comment, 250)}</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── LLM Report ────────────────────────────────────────────────────────────
    st.subheader("📋 Reputation Report")
    def format_report(text: str) -> str:
        """Converts plain text report into styled HTML."""
        lines = text.strip().split("\n")
        html = []
        for line in lines:
            line = line.strip()
            if not line:
                html.append("<br>")
            elif line.isupper() or (len(line) < 60 and line.endswith(":")):
                # It's a heading
                html.append(f'<p style="color:#667eea;font-weight:600;font-size:1rem;margin:20px 0 6px 0;letter-spacing:0.05em;">{line}</p>')
            elif line.startswith("-") or line.startswith("•"):
                # It's a bullet
                html.append(f'<p style="margin:4px 0 4px 24px;color:#c8c8e0;">• {line.lstrip("-•").strip()}</p>')
            else:
                html.append(f'<p style="margin:4px 0;color:#c8c8e0;">{line}</p>')
        return "".join(html)

    st.markdown(
        f'<div class="report-box">{format_report(report)}</div>',
        unsafe_allow_html=True,
    )

    # Download button
    st.download_button(
        label="⬇️ Download Report",
        data=report,
        file_name="reputation_report.txt",
        mime="text/plain",
        use_container_width=True,
    )