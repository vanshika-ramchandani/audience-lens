## 🚀 Live Demo
https://audience-lens-nckdhnkm6fgnu9ryzbtrzf.streamlit.app/


## 🔍 AudienceLens

> **AI-powered YouTube comment intelligence for brands, creators, and marketers.**

AudienceLens analyzes YouTube video comments using NLP and LLM to surface what your audience is *actually* saying — broken down into themes, sentiment, and actionable recommendations. No more manually scrolling through thousands of comments.

---

## ✨ Features

- **Smart Comment Fetching** — Pulls up to 500 comments from any YouTube video using the official YouTube Data API
- **Intelligent Filtering** — Removes spam, bots, and low-quality comments automatically
- **Semantic Theme Clustering** — Groups comments into 3–6 meaningful themes using transformer embeddings (not just keywords)
- **Multilingual Sentiment Analysis** — Accurately classifies sentiment in English, Hindi, and Hinglish using LLM
- **AI-Generated Theme Names** — Each cluster gets a human-readable name like "Delivery Speed Complaints" or "Product Quality Praise"
- **Brand Reputation Report** — LLM-generated summary with key concerns and actionable recommendations
- **Severity Assessment** — Automatically flags reputation health as Healthy, Needs Attention, or Critical
- **Download Report** — Export the full reputation report as a `.txt` file

---

## 🧠 How It Works

```
User pastes YouTube URL
        ↓
Fetch up to 500 comments (YouTube Data API v3)
        ↓
Clean & filter comments (remove spam, short/irrelevant comments)
        ↓
Generate semantic embeddings (Sentence Transformers - MiniLM)
        ↓
Cluster into themes (KMeans)
        ↓
Analyze sentiment per cluster (Groq LLaMA 3.3)
        ↓
Label themes with AI (Groq LLaMA 3.3)
        ↓
Generate reputation report (Groq LLaMA 3.3)
        ↓
Display interactive dashboard (Streamlit)
```

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Frontend | Streamlit | Interactive web UI |
| Comment Fetching | YouTube Data API v3 | Official comment data |
| Text Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) | Semantic understanding of comments |
| Clustering | KMeans (scikit-learn) | Grouping similar comments into themes |
| Sentiment & LLM | Groq (LLaMA 3.3 70B) | Multilingual sentiment + report generation |
| Environment | python-dotenv | Secure API key management |

---

## 📁 Project Structure

```
AudienceLens/
│
├── app.py                  # Streamlit frontend & pipeline orchestration
│
├── agent/
│   ├── fetcher.py          # YouTube API — fetch & extract comments
│   ├── preprocessor.py     # Clean, filter & normalize comments
│   ├── clustering.py       # Embed comments & cluster into themes
│   ├── sentiment.py        # LLM-based multilingual sentiment analysis
│   └── summarizer.py       # Theme naming & reputation report generation
│
├── utils/
│   └── helpers.py          # Shared utility functions
│
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
│
├── .env.example            # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- YouTube Data API v3 key
- Groq API key

### 1. Clone the repository
```bash
git clone https://github.com/vanshika-ramchandani/audience-lens
cd audience-lens
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API keys
```bash
cp .env.example .env
```

Open `.env` and fill in your keys:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 Getting API Keys

**YouTube Data API v3 (Free)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Search and enable **"YouTube Data API v3"**
4. Go to Credentials → Create Credentials → API Key
5. Restrict the key to YouTube Data API v3 only

> Free quota: 10,000 units/day. Fetching 500 comments costs ~5 units.

**Groq API (Free)**
1. Sign up at [console.groq.com](https://console.groq.com/)
2. Go to API Keys → Create new key

> Free tier is more than sufficient for this project.

---

## 📊 Example Output
<img width="1912" height="857" alt="Screenshot 2026-05-11 125948" src="https://github.com/user-attachments/assets/49d28a2e-187f-4663-b0f4-6c318a7338af" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img width="1916" height="875" alt="Screenshot 2026-05-11 125914" src="https://github.com/user-attachments/assets/e292fe0c-0a70-4260-897a-f348d9844aef" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img width="1914" height="862" alt="Screenshot 2026-05-11 125935" src="https://github.com/user-attachments/assets/479a34e2-b92c-42b2-8b73-d4247b586037" />


### Overview Metrics
| Metric | Description |
|---|---|
| Comments Analyzed | Total valid comments processed |
| Themes Found | Number of distinct comment clusters |
| Positive Sentiment | Overall weighted positive % |
| Reputation Health | Healthy / Needs Attention / Critical |

### Comment Themes

Each theme card shows:
- Theme name (AI-generated)
- Dominant sentiment
- Positive/Negative breakdown
- Top 5 most-liked comments in that theme

### Reputation Report

LLM-generated report covering:
- **Reputation Summary** — Overall audience perception
- **Key Concerns** — Main issues and complaints
- **Recommendations** — Specific actions for the brand

---

## 💡 Use Cases

- **Brands** — Understand what customers say after a product launch video
- **Creators** — Know exactly what your audience wants more of
- **Marketers** — Analyze competitor video comments for market research
- **PR Teams** — Monitor reputation after a campaign or controversy
- **Agencies** — Generate client reputation reports in minutes instead of hours

---

## ⚠️ Limitations

- Analyzes YouTube comments only (Instagram/TikTok APIs are too restrictive)
- YouTube API free quota: 10,000 units/day
- Groq free tier has rate limits — analyzing 500 comments takes ~30–60 seconds
- Sentiment accuracy on very short comments (under 3 words) may vary

---

## 🔮 Future Improvements

- [ ] Channel-level analysis (aggregate across multiple videos)
- [ ] Trend tracking over time (compare sentiment across video uploads)
- [ ] Support for multiple languages with language detection
- [ ] Competitor comparison (analyze two channels side by side)

---

## 👩‍💻 Author

**Vanshika Ramchandani**
