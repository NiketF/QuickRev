import pandas as pd
import random

def load_demo_dataset():
    """Generates a realistic dataset of 500 reviews for reliable offline testing."""
    
    positive_templates = [
        "Absolutely love this! The battery life is phenomenal.",
        "Great value for money. The camera exceeds my expectations.",
        "Performance is blazing fast. Highly recommended.",
        "Solid build quality and very responsive.",
        "Exactly what I was looking for. Five stars!",
        "The display is crisp and clear. Best purchase this year."
    ]
    
    neutral_templates = [
        "It's okay. Does the job but nothing special.",
        "Average product. The packaging was a bit damaged.",
        "Not bad, but I expected a bit more for the price.",
        "It works fine, but the setup was complicated.",
        "Decent features, but the battery drains faster than advertised."
    ]
    
    negative_templates = [
        "Terrible experience. Heats up within 10 minutes of use.",
        "Do not buy! The screen cracked easily and customer support is awful.",
        "Very laggy and slow charging. Completely regret this purchase.",
        "Defective item received. Waste of money.",
        "The software is buggy and crashes constantly."
    ]

    reviews = []
    
    # Generate 500 reviews to trigger the 20% sampling logic (100 sampled reviews)
    for i in range(500):
        # 60% Positive, 20% Neutral, 20% Negative distribution
        rand_val = random.random()
        if rand_val < 0.6:
            text = random.choice(positive_templates)
        elif rand_val < 0.8:
            text = random.choice(neutral_templates)
        else:
            text = random.choice(negative_templates)
            
        # Add some random noise/words to make them unique
        noise = [" Seriously.", " Wow.", " Man.", " Just wow.", " Ugh.", " Sigh.", ""]
        text += random.choice(noise)
        
        reviews.append({
            "review_title": f"Review {i}",
            "review_text": text,
            "rating": None
        })
        
    return pd.DataFrame(reviews)