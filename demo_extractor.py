import pandas as pd
from scraper import extract_amazon_reviews, extract_flipkart_reviews

def save_sample_from_url(url, filename="demo_reviews.csv"):
    """Scrapes a small sample of real reviews and saves them to a CSV."""
    print(f"⏳ Extracting real reviews from: {url}")
    
    # We limit to 2 pages just to get a quick, real sample
    if "amazon" in url.lower():
        df = extract_amazon_reviews(url, max_pages=2)
    elif "flipkart" in url.lower():
        df = extract_flipkart_reviews(url, max_pages=2)
    else:
        print("❌ Unsupported URL. Please use Amazon or Flipkart.")
        return

    if not df.empty:
        df.to_csv(filename, index=False)
        print(f"✅ Success! {len(df)} real reviews saved to '{filename}'.")
        print("You can now load this file in the main application.")
    else:
        print("❌ Failed to extract reviews. The site might have blocked the request.")

if __name__ == "__main__":
    # Example usage: Replace this URL with any product you want to test
    test_url = "https://www.amazon.in/dp/B0CHX1W1XY" 
    save_sample_from_url(test_url)