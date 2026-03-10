import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

def extract_amazon_reviews(url, max_pages=3):
    """Extracts Amazon reviews using the Real-Time Amazon Data API."""
    print(f"🚀 Fetching up to {max_pages} pages of live recent reviews via RapidAPI...")
    
    # Extract ASIN from the URL
    try:
        if "/dp/" in url:
            asin = url.split("/dp/")[1].split("/")[0][:10]
        elif "/product-reviews/" in url:
            asin = url.split("/product-reviews/")[1].split("/")[0][:10]
        else:
            print("Could not find ASIN in URL.")
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    # Your API Credentials
    API_KEY = os.getenv('RAPIDAPI_KEY')
    API_HOST = os.getenv('RAPIDAPI_HOST')
    API_ENDPOINT = f"https://{API_HOST}/product-reviews"

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    reviews = []
    
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...")
        querystring = {
            "asin": asin,
            "country": "IN", 
            "page": str(page),
            "sort_by": "MOST_RECENT", # Grabs the raw, unfiltered latest reviews
            "star_rating": "ALL",
            "verified_purchases_only": "false",
            "images_or_videos_only": "false",
            "current_format_only": "false"
        }
        
        try:
            response = requests.get(API_ENDPOINT, headers=headers, params=querystring, timeout=15)
            
            if response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text}")
                break
                
            json_data = response.json()
            
            # The API usually nests reviews inside a 'data' object
            api_data = json_data.get('data', {})
            api_reviews = api_data.get('reviews', [])
            
            if not api_reviews:
                print("No more reviews found. Stopping pagination.")
                break
                
            for rev in api_reviews:
                reviews.append({
                    "review_title": rev.get('review_title', 'No Title'),
                    "review_text": rev.get('review_comment', rev.get('review_text', '')), 
                    "rating": rev.get('review_star_rating', None)
                })
                
        except Exception as e:
            print(f"API Extraction Error on page {page}: {e}")
            break
            
        # Pause for 1 second before requesting the next page to avoid rate limits
        time.sleep(1)

    df = pd.DataFrame(reviews)
    print(f"✅ Successfully extracted {len(df)} reviews.")
    return df


def extract_flipkart_reviews(url, max_pages=2):
    """Placeholder for Flipkart reviews to prevent import errors in app.py."""
    print("Flipkart API integration pending. Falling back to empty dataframe.")
    return pd.DataFrame()


if __name__ == "__main__":
    test_url = "https://www.amazon.in/dp/B0CHX1W1XY"
    print("Testing API Integration...")
    
    # Run the extraction for 2 pages to test pagination and the sleep function
    df_test = extract_amazon_reviews(test_url, max_pages=2)
    
    if not df_test.empty:
        print("\n✅ SUCCESS! Data extracted:")
        print(df_test.head())
    else:
        print("\n❌ FAILED. The DataFrame is empty. Check your API credentials or parameters.")