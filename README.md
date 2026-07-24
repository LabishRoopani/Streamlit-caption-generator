# ✨ Social Caption Generator

> **Qodex Software Internship Task 2** — Wrap the Task 1 AI script in a robust Streamlit web UI deployable by non-technical users.

## 🎥 Demo Video
**Watch the walkthrough here:** [Loom Video Link](https://www.loom.com/share/d1ebd3b838034c7e9342f58c41122ad6)

---

## 🚀 Features
- **AI-Powered Captions** — Uses Google Gemini 3.5 Flash to generate 5 unique captions per product
- **3 Tone Modes** — Funny, Professional, Luxury
- **Batch Mode** — Enter multiple products (one per line) and generate captions for all of them
- **Progress Bar** — Live progress bar during batch processing
- **Retry Logic** — Automatically retries on rate limit errors (429) — never crashes
- **Token & Cost Logging** — Logs exact token usage and estimated cost per request to the terminal

---

## 💻 Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key
Create a `.env.local` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Start the app
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub (public repository)
2. Go to [share.streamlit.io](https://share.streamlit.io/) → **Create app**
3. Select this repository and set main file to `app.py`
4. Under **Advanced Settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
5. Click **Deploy** ✅

---

## 💰 Estimated Monthly API Costs (Gemini 3.5 Flash)

Token usage is logged on every request in the server terminal. Below is the cost breakdown:

| Metric | Pricing |
|---|---|
| Input tokens | $0.075 per 1M tokens |
| Output tokens | $0.30 per 1M tokens |

**Per-request estimate** (5 captions):
- Average input: ~100 tokens → **$0.0000075**
- Average output: ~200 tokens → **$0.000060**
- **Total per request: ~$0.000068**

**Monthly estimates:**

| Usage | Requests/month | Est. Monthly Cost |
|---|---|---|
| Light (Personal) | 1,000 | **$0.07** |
| Medium (Small Business) | 10,000 | **$0.68** |
| Heavy (Agency) | 100,000 | **$6.80** |

**Conclusion: This tool is extremely affordable — a full agency running 100k requests would spend under $7/month.**
