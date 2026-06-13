import re
import pandas as pd
import nltk
import streamlit as st
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from collections import Counter

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Twitter Sentiment Analyzer",
    page_icon="📈",
    layout="wide"
)

# ====================== LOAD VADER ======================
@st.cache_resource
def load_vader():
    nltk.download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()

sia = load_vader()

# ====================== CLEANING FUNCTION ======================
@st.cache_data
def clean_tweet_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = text.replace('#', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ====================== SENTIMENT LABEL ======================
def get_sentiment_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# ====================== TITLE ======================
st.title("📈 Twitter Sentiment Analysis Dashboard")
st.markdown("Analyze tweets using **VADER Sentiment Analysis**")

st.markdown("---")

# ====================== SINGLE TWEET ANALYZER ======================
st.subheader("📝 Real-Time Single Tweet Analyzer")

tweet_input = st.text_area("Enter a tweet:", height=120)

if st.button("Analyze Tweet"):
    if tweet_input.strip():
        cleaned = clean_tweet_text(tweet_input)
        score = sia.polarity_scores(cleaned)["compound"]
        sentiment = get_sentiment_label(score)

        st.success(f"**Sentiment:** {sentiment}")
        st.metric("Compound Score", f"{score:.3f}")
        st.text_area("Cleaned Text:", cleaned, height=80, disabled=True)
    else:
        st.warning("Please enter some text.")

st.markdown("---")

# ====================== SIDEBAR ======================
st.sidebar.header("📥 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file:
    st.sidebar.success(f"File: {uploaded_file.name}")

# ====================== MAIN PROCESSING ======================
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)

        st.sidebar.info(f"Total rows: **{len(raw_df):,}**")

        column_options = raw_df.columns.tolist()
        text_column = st.sidebar.selectbox("Select Tweet Text Column", column_options)

        max_rows = st.sidebar.slider(
            "Maximum tweets to analyze", 
            min_value=500, 
            max_value=100000, 
            value=10000, 
            step=500
        )

        if st.button("🚀 Start Analysis", type="primary"):
            with st.spinner(f"Processing up to {max_rows:,} tweets..."):
                
                df = raw_df.head(max_rows).copy()

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Cleaning
                status_text.text("Cleaning tweets...")
                df["Cleaned Text"] = df[text_column].apply(clean_tweet_text)
                df = df[df["Cleaned Text"] != ""].reset_index(drop=True)

                # Sentiment Analysis
                status_text.text("Running Sentiment Analysis...")
                compound_scores = []
                for idx, text in enumerate(df["Cleaned Text"]):
                    score = sia.polarity_scores(text)["compound"]
                    compound_scores.append(score)
                    
                    if idx % max(1, len(df)//20) == 0:
                        progress_bar.progress(min(1.0, (idx + 1) / len(df)))

                df["Compound Score"] = compound_scores
                df["Sentiment"] = df["Compound Score"].apply(get_sentiment_label)

                progress_bar.progress(1.0)
                status_text.success("✅ Analysis Completed!")

                # Filters
                st.subheader("🔍 Filters")
                col1, col2 = st.columns(2)
                with col1:
                    keyword = st.text_input("Search Keyword")
                with col2:
                    sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Neutral", "Negative"])

                filtered_df = df.copy()
                if keyword:
                    filtered_df = filtered_df[filtered_df["Cleaned Text"].str.contains(keyword.lower(), na=False)]
                if sentiment_filter != "All":
                    filtered_df = filtered_df[filtered_df["Sentiment"] == sentiment_filter]

                # Metrics
                total = len(filtered_df)
                if total > 0:
                    pos = len(filtered_df[filtered_df["Sentiment"] == "Positive"])
                    neu = len(filtered_df[filtered_df["Sentiment"] == "Neutral"])
                    neg = len(filtered_df[filtered_df["Sentiment"] == "Negative"])

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Tweets", f"{total:,}")
                    c2.metric("Positive", f"{pos:,} ({pos/total*100:.1f}%)")
                    c3.metric("Neutral", f"{neu:,} ({neu/total*100:.1f}%)")
                    c4.metric("Negative", f"{neg:,} ({neg/total*100:.1f}%)")

                    st.markdown("---")

                    # Charts
                    left, right = st.columns(2)
                    dist = filtered_df["Sentiment"].value_counts()
                    with left:
                        st.subheader("📊 Bar Chart")
                        st.bar_chart(dist)
                    with right:
                        st.subheader("🥧 Pie Chart")
                        fig, ax = plt.subplots()
                        ax.pie(dist, labels=dist.index, autopct="%1.1f%%")
                        st.pyplot(fig)

                    # Top Tweets
                    col_pos, col_neg = st.columns(2)
                    with col_pos:
                        st.subheader("😀 Top Positive")
                        st.dataframe(filtered_df.nlargest(5, "Compound Score")[[text_column, "Compound Score"]])
                    with col_neg:
                        st.subheader("😠 Top Negative")
                        st.dataframe(filtered_df.nsmallest(5, "Compound Score")[[text_column, "Compound Score"]])

                    # Word Cloud
                    st.subheader("☁️ Word Cloud")
                    all_text = " ".join(filtered_df["Cleaned Text"])
                    if all_text:
                        wc = WordCloud(width=1200, height=600, background_color="white").generate(all_text)
                        fig2, ax2 = plt.subplots(figsize=(12, 6))
                        ax2.imshow(wc)
                        ax2.axis("off")
                        st.pyplot(fig2)

                    # Common Words
                    st.subheader("🔥 Top Keywords")
                    words = all_text.split()
                    common = Counter(words).most_common(15)
                    st.dataframe(pd.DataFrame(common, columns=["Word", "Count"]))

                    # Download
                    st.download_button(
                        "📥 Download Results",
                        filtered_df.to_csv(index=False).encode('utf-8'),
                        "sentiment_results.csv",
                        "text/csv"
                    )

    except Exception as e:
        st.error(f"Error: {str(e)}")

else:
    st.info("👈 Upload a CSV or Excel file from the sidebar to start.")