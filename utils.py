import pandas as pd

def clean_data(df):
    """Cleans the review dataframe."""
    if df.empty or 'review_text' not in df.columns:
        return df
        
    # Drop rows where review_text is empty or NaN
    df = df.dropna(subset=['review_text'])
    df = df[df['review_text'].str.strip() != '']
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['review_text'])
    
    # Trim whitespace and normalize text (lowercase for consistent processing later)
    df['review_text'] = df['review_text'].str.strip()
    
    return df

def sample_reviews(df):
    """Samples 20% of the dataset if total reviews > 50."""
    total_reviews = len(df)
    
    if total_reviews > 50:
        # Deterministic random seed
        sampled_df = df.sample(frac=0.20, random_state=42)
        return sampled_df, total_reviews
    
    return df, total_reviews