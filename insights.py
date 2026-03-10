import re
from collections import Counter

# Standard English stop words
STOP_WORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs", 
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", 
    "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", 
    "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", 
    "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", 
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", 
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", 
    "will", "just", "don", "should", "now", "product", "phone", "item", "good", "bad", "buy"
])

def extract_keywords(df, sentiment_filter, top_n=5):
    """Extracts top keywords for a specific sentiment."""
    filtered_texts = df[df['sentiment'] == sentiment_filter]['review_text'].tolist()
    text_corpus = " ".join(filtered_texts).lower()
    
    # Extract words using regex
    words = re.findall(r'\b[a-z]{3,}\b', text_corpus)
    
    # Filter stopwords
    meaningful_words = [word for word in words if word not in STOP_WORDS]
    
    # Count frequencies
    word_counts = Counter(meaningful_words)
    return word_counts.most_common(top_n)

def get_highlights(df):
    """Returns top positive and negative reviews based on VADER score."""
    if df.empty:
        return [], []
        
    # First, separate the reviews by their actual sentiment
    pos_df = df[df['sentiment'] == 'Positive']
    neg_df = df[df['sentiment'] == 'Negative']
    
    # Extract the highest scores from the Positive pool
    if not pos_df.empty:
        top_pos = pos_df.nlargest(3, 'vader_score')['review_text'].tolist()
    else:
        top_pos = ["No positive reviews found in this dataset."]
        
    # Extract the lowest scores from the Negative pool
    if not neg_df.empty:
        top_neg = neg_df.nsmallest(3, 'vader_score')['review_text'].tolist()
    else:
        top_neg = ["No negative reviews found in this dataset. This product is highly rated!"]
        
    return top_pos, top_neg