import streamlit as st
import pandas as pd
import os # NEW IMPORT
import plotly.express as px
from scraper import extract_amazon_reviews
from utils import clean_data, sample_reviews
from sentiment import analyze_sentiment, calculate_metrics
from insights import extract_keywords, get_highlights

st.set_page_config(page_title="QuickRev AI", layout="wide", page_icon="📊")

# --- HEADER ---
st.title("📊 QuickRev AI – Smart Product Review Analyzer")
st.markdown("Instantly analyze thousands of e-commerce product reviews to uncover sentiment, trends, and product recommendations without reading them manually.")

# --- INPUT PANEL ---
st.sidebar.header("Input Data")
input_method = st.sidebar.radio(
    "Choose Input Method:", 
    ("Live Product URL", "Load Cached Dataset", "Manual Reviews")
)

df = pd.DataFrame()

if input_method == "Load Cached Dataset":
    st.sidebar.info("📂 Loads real product reviews previously extracted via 'demo_extractor.py'.")
    analyze_btn = st.sidebar.button("Analyze Cached Data")
    
    if analyze_btn:
        if os.path.exists("demo_reviews.csv"):
            df = pd.read_csv("demo_reviews.csv")
            st.toast("Cached data loaded successfully!", icon="✅")
        else:
            st.error("⚠️ 'demo_reviews.csv' not found. Please run `python demo_extractor.py` first to generate the file.")

elif input_method == "Live Product URL":
    url = st.sidebar.text_input("Paste Amazon or Flipkart Product URL:")
    analyze_btn = st.sidebar.button("Analyze URL")
    
    if analyze_btn and url:
        with st.spinner("Scraping live reviews... Please wait."):
            if "amazon" in url.lower():
                df = extract_amazon_reviews(url,max_pages=3)
            else:
                st.sidebar.error("Unsupported URL.")
                
        if df.empty:
            st.error("⚠️ Live scraping blocked. Please use the 'Load Cached Dataset' option.")
            
elif input_method == "Manual Reviews":
    manual_text = st.sidebar.text_area("Paste reviews (one per line):", height=200)
    analyze_btn = st.sidebar.button("Analyze Text")
    
    if analyze_btn and manual_text:
        reviews_list = [r.strip() for r in manual_text.split('\n') if r.strip()]
        df = pd.DataFrame({"review_text": reviews_list})

# ... (The rest of the app.py PROCESSING & RESULTS DASHBOARD code remains exactly the same) ...
# --- PROCESSING & RESULTS DASHBOARD ---
if not df.empty:
    with st.spinner("Cleaning and Analyzing Data..."):
        # Clean
        df = clean_data(df)
        
        # Sample
        sampled_df, original_total = sample_reviews(df)
        
        if len(sampled_df) < original_total:
            st.info(f"⚡ **Performance Optimization Active:** Analyzing {len(sampled_df):,} sampled reviews from {original_total:,} total reviews to maintain statistical reliability and speed.")
            
        # Sentiment Analysis
        analyzed_df = analyze_sentiment(sampled_df)
        total_revs, pos_pct, neg_pct, neu_pct, sentiment_score = calculate_metrics(analyzed_df)
        
    st.markdown("---")
    
    # --- METRICS CARDS ---
    st.subheader("Overview Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Reviews Analyzed", f"{total_revs:,}")
    col2.metric("Positive %", f"{pos_pct:.1f}%")
    col3.metric("Neutral %", f"{neu_pct:.1f}%")
    col4.metric("Negative %", f"{neg_pct:.1f}%")
    col5.metric("Sentiment Score", f"{sentiment_score:.2f}")

    # --- PRODUCT RECOMMENDATION ---
    st.markdown("### 💡 Product Recommendation")
    if sentiment_score > 0.4:
        st.success("✅ **RECOMMENDED:** This product has strong positive sentiment.")
    elif 0.1 <= sentiment_score <= 0.4:
        st.warning("🤔 **CONSIDER:** This product has mixed to slightly positive feedback.")
    else:
        st.error("❌ **AVOID:** This product has predominantly negative feedback.")

    st.markdown("---")
    
    # --- CHARTS SECTION ---
    st.subheader("Visual Analytics")
    c1, c2 = st.columns(2)
    
    sentiment_counts = analyzed_df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    with c1:
        # Sentiment Pie Chart
        fig_pie = px.pie(sentiment_counts, values='Count', names='Sentiment', 
                         title='Sentiment Distribution',
                         color='Sentiment',
                         color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#95a5a6', 'Negative':'#e74c3c'})
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Sentiment Bar Chart
        fig_bar = px.bar(sentiment_counts, x='Sentiment', y='Count',
                         title='Volume by Sentiment',
                         color='Sentiment',
                         color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#95a5a6', 'Negative':'#e74c3c'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- INSIGHTS SECTION ---
    st.markdown("---")
    st.subheader("Key Themes & Keywords")
    
    top_pos_words = extract_keywords(analyzed_df, "Positive", 10)
    top_neg_words = extract_keywords(analyzed_df, "Negative", 10)
    
    kw_col1, kw_col2 = st.columns(2)
    with kw_col1:
        st.write("**Top Positive Themes (Pros)**")
        if top_pos_words:
            df_pos_words = pd.DataFrame(top_pos_words, columns=['Word', 'Frequency'])
            fig_pos = px.bar(df_pos_words, x='Frequency', y='Word', orientation='h', color_discrete_sequence=['#2ecc71'])
            fig_pos.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_pos, use_container_width=True)
        else:
            st.write("Not enough data.")
            
    with kw_col2:
        st.write("**Top Negative Themes (Cons)**")
        if top_neg_words:
            df_neg_words = pd.DataFrame(top_neg_words, columns=['Word', 'Frequency'])
            fig_neg = px.bar(df_neg_words, x='Frequency', y='Word', orientation='h', color_discrete_sequence=['#e74c3c'])
            fig_neg.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_neg, use_container_width=True)
        else:
            st.write("Not enough data.")

    # --- REVIEW HIGHLIGHTS ---
    st.markdown("---")
    st.subheader("Review Highlights")
    top_pos_reviews, top_neg_reviews = get_highlights(analyzed_df)
    
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.success("**Strongest Positive Reviews**")
        for rev in top_pos_reviews:
            st.info(f'"{rev}"')
            
    with h_col2:
        st.error("**Strongest Negative Reviews**")
        for rev in top_neg_reviews:
            st.warning(f'"{rev}"')

    # --- REVIEW EXPLORER ---
    st.markdown("---")
    st.subheader("Raw Review Explorer")
    st.dataframe(analyzed_df[['review_text', 'sentiment', 'vader_score']], use_container_width=True, height=300)

elif input_method == "Manual Reviews" and not manual_text:
    st.info("👈 Please enter review texts in the sidebar and click 'Analyze Text'.")