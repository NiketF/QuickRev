from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import re

analyzer = SentimentIntensityAnalyzer()

# Fatal phrases that instantly ruin a product experience, regardless of positive fluff.
FATAL_NEGATIVE_PHRASES = [
    "stopped working", "not a good", "worst", "terrible", "waste of money", 
    "don't buy", "do not buy", "defective", "broken", "useless", "disappointed",
    "lack of", "poor quality", "garbage", "return", "refund"
]

def extract_numeric_rating(rating_val):
    """Safely extracts the float value from Amazon rating strings (e.g. '1.0 out of 5 stars')."""
    if pd.isna(rating_val) or rating_val is None:
        return None
    try:
        match = re.search(r'\d+(\.\d+)?', str(rating_val))
        if match:
            return float(match.group())
    except:
        pass
    return None

def analyze_sentiment(df):
    """Adds sentiment classification using a Hybrid VADER + Rating approach."""
    sentiments = []
    compound_scores = []
    
    # Ensure rating column exists (especially for manual input where it might be missing)
    if 'rating' not in df.columns:
        df['rating'] = None

    for index, row in df.iterrows():
        text = str(row['review_text'])
        raw_rating = row['rating']
        
        # 1. Base VADER Score
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # 2. Smart Keyword Penalty (Fixes VADER's blind spot for "mixed" reviews)
        text_lower = text.lower()
        for phrase in FATAL_NEGATIVE_PHRASES:
            if phrase in text_lower:
                compound -= 0.6  # Apply a heavy mathematical penalty
        
        # Cap the compound score so it stays mathematically valid between -1.0 and 1.0
        compound = max(min(compound, 1.0), -1.0)
        
        # 3. Final Determination Engine
        num_rating = extract_numeric_rating(raw_rating)
        
        # If Amazon provided a star rating, treat it as the absolute truth
        if num_rating is not None:
            if num_rating <= 2.5:
                final_sentiment = 'Negative'
                if compound > 0: compound = -0.5 # Force score negative for the UI
            elif num_rating >= 4.0:
                final_sentiment = 'Positive'
                if compound < 0: compound = 0.5  # Force score positive for the UI
            else:
                final_sentiment = 'Neutral'
        else:
            # Fallback to heavily-penalized VADER if no star rating exists (Manual Input)
            if compound >= 0.05:
                final_sentiment = 'Positive'
            elif compound <= -0.05:
                final_sentiment = 'Negative'
            else:
                final_sentiment = 'Neutral'
                
        sentiments.append(final_sentiment)
        compound_scores.append(compound)
        
    df['sentiment'] = sentiments
    df['vader_score'] = compound_scores
    return df

def calculate_metrics(df):
    """Calculates overall metrics based on requirements."""
    total_reviews = len(df)
    if total_reviews == 0:
        return 0, 0, 0, 0, 0
        
    pos_count = len(df[df['sentiment'] == 'Positive'])
    neg_count = len(df[df['sentiment'] == 'Negative'])
    neu_count = len(df[df['sentiment'] == 'Neutral'])
    
    pos_pct = (pos_count / total_reviews) * 100
    neg_pct = (neg_count / total_reviews) * 100
    neu_pct = (neu_count / total_reviews) * 100
    
    sentiment_score = (pos_count - neg_count) / total_reviews
    
    return total_reviews, pos_pct, neg_pct, neu_pct, sentiment_score