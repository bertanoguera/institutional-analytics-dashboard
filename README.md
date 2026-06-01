# Institutional Analytics Dashboard

Interactive dashboard built with Plotly Dash extending a prior set of static learning analytics visualizations into an explorable interface, designed to support users with different levels of visualization literacy. Covers four analytical cases using simulated data — student satisfaction, academic performance, LMS engagement, and task diversity across teaching methodologies. A conversational AI assistant (Google Gemini) is embedded in the interface to let users filter the charts and ask interpretive questions in plain language.

## Cases

- **Case 1** — Student satisfaction with teaching, broken down by professor gender, student gender, and faculty
- **Case 2** — Student academic performance by teaching methodology and workload satisfaction
- **Case 3** — Social comparison of courses with high LMS interaction against the institutional average
- **Case 4** — Diversity of LMS task types by teaching methodology and workload satisfaction

## AI Assistant

Each case includes a chat panel powered by the Google Gemini API. The assistant can:

- Filter any chart by group, methodology, course, or indicator using plain-language queries
- Answer factual questions about the data (e.g. "what is the highest value for lectures?")
- Explain metrics, visualisation choices, and responsible interpretation factors
- Accumulate filters across turns — new queries refine the active view without resetting it
- Reset to the full dataset when asked, or via the Reset filters button

## Installation

Make sure you have Python installed, then run:

```
pip install -r requirements.txt
```

Copy the environment variable template and add your Gemini API key:

```
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your real key. The file is excluded from version control and never committed.

## Usage

```
python app.py
```

Then open your browser and go to `http://127.0.0.1:8050`

## Notes

All data used in this dashboard is artificially simulated for demonstration and research purposes only.
