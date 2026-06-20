# Twitter Sentiment Analysis Dashboard

A Streamlit-based Twitter Sentiment Analysis application that analyzes tweets using NLTK's VADER sentiment engine.

## Features

- Real-Time Tweet Analysis
- CSV Upload Support
- Excel Upload Support
- Optional Live X Search via Xquik
- Sentiment Classification
  - Positive
  - Negative
  - Neutral
- Interactive Dashboard
- Sentiment Distribution Charts
- Pie Charts
- Word Cloud Visualization
- Top Positive Tweets
- Top Negative Tweets
- Keyword Frequency Analysis
- CSV Export

## Technologies Used

- Python
- Streamlit
- Pandas
- NLTK
- Matplotlib
- WordCloud
- Xquik

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/twitter-sentiment-analysis.git
cd twitter-sentiment-analysis
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional live X search:

```bash
export XQUIK_API_KEY=your_xquik_api_key
```

Run application:

```bash
streamlit run app.py
```

## Project Structure

```

Twitter-Sentiment-Analysis/

├── app.py
├── README.md
├── requirements.txt
├── data/
├── notebooks/
├── models/
└── .gitignore

```

## Sample Dataset Format

| Tweet |
|---------|
| I love this product |
| Terrible customer service |
| Average experience |
