# Blinkit Category Discovery Engine

AI-powered analysis of real user feedback to understand why Blinkit users repeat-buy the same
categories and what would move them to explore new ones — built for the Blinkit Growth Team
graduation project.

This repository ships with one curated, validated analysis run (1,176 reviews collected, 189
tagged with high-confidence behavioral signal) so the dashboard opens fully populated. A live
analyzer is also included so reviewers can test the exact extraction workflow on any review.

## What's inside

- **Insights Dashboard** — the full validated analysis: theme distribution, user segments,
  category risk breakdown, and answers to all 8 brief research questions, each with supporting
  evidence and a PM implication.
- **Live Analyzer** — paste any review, run the same structured-extraction prompt used on the
  full dataset, and see it tagged in real time.
- **Methodology & Validation** — how data was filtered before AI touched it, how themes were
  extracted, and documented limitations (source bias, signal rate, duplicate content).

## Data sources analyzed

| Source | Records | Notes |
| --- | --- | --- |
| Google Play | 662 | Largest volume; skews toward short one-word ratings |
| Reddit | 360 | Candid discussion; mostly post titles rather than full bodies |
| YouTube comments | 144 | Includes industry-economics debate, filtered for relevance |
| App Store | 10 | Small sample — treated as directional only |

## Pipeline

1. **Collect** — reviews gathered across the 4 sources above
2. **Filter** — off-topic content (labor/picker posts, industry debate) and bare statements with
   no reasoning are excluded before AI extraction
3. **Extract** — a single controlled Gemini prompt tags each review with: repeat-buying signal,
   category, barrier, reason type, actionable "what would build trust," user segment, a grounding
   quote, and a confidence score
4. **Validate** — every tag requires an exact supporting quote (no fabricated reasoning); a sample
   was manually re-read against source text; near-duplicate/viral content is flagged, not silently
   counted

Full methodology, including known limitations, is documented inside the app's
**Methodology & Validation** section.

## Required secret

| Secret | Required for | Notes |
| --- | --- | --- |
| `GEMINI_API_KEY` | Live Analyzer tab | Get a free key at aistudio.google.com/apikey |

This app does not require the key to view the Insights Dashboard — only to test the Live
Analyzer. The key can be entered directly in the app, or configured via
`.streamlit/secrets.toml` (see below) so reviewers don't need their own key.

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub
2. On share.streamlit.io, create a new app pointing to `app.py`
3. (Optional) Add `GEMINI_API_KEY` under app Settings → Secrets so the Live Analyzer works
   without reviewers needing their own key:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Deploy — the Insights Dashboard loads immediately with the packaged dataset

## Repository structure

```
app.py                 # Streamlit application (dashboard + live analyzer)
tagged_reviews.csv      # Validated analysis output — 189 tagged records
requirements.txt        # Python dependencies
```

## Project brief alignment

This engine answers the 8 required research questions:
why users repeat-buy the same categories, what prevents exploring new ones, how users discover
products today, the role of habit, what information users need before trying a new category,
recurring frustrations, which segments are more likely to experiment, and what unmet needs emerge
consistently — each backed by evidence and a stated confidence level, not assumption.
