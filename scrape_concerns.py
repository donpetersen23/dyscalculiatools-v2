import requests
from bs4 import BeautifulSoup
import json
from collections import Counter
import re

def scrape_reddit(subreddit, query, limit=100):
    """Scrape Reddit posts and comments"""
    concerns = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f'https://www.reddit.com/r/{subreddit}/search.json?q={query}&limit={limit}&sort=relevance'
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for post in data['data']['children']:
                title = post['data']['title']
                selftext = post['data'].get('selftext', '')
                concerns.append(title + ' ' + selftext)
    except Exception as e:
        print(f"Error scraping r/{subreddit}: {e}")
    
    return concerns

def extract_concerns(texts):
    """Extract concern keywords and phrases"""
    concern_keywords = [
        'multiplication', 'division', 'addition', 'subtraction', 'times tables',
        'math facts', 'counting', 'numbers', 'fractions', 'decimals',
        'word problems', 'story problems', 'time', 'clock', 'money',
        'anxiety', 'confidence', 'frustration', 'memory', 'remembering',
        'sequencing', 'steps', 'procedures', 'spatial', 'visual',
        'estimation', 'quantity', 'magnitude', 'place value',
        'negative numbers', 'algebra', 'geometry', 'measurement'
    ]
    
    concerns = []
    for text in texts:
        text = text.lower()
        for keyword in concern_keywords:
            if keyword in text:
                concerns.append(keyword)
    
    return concerns

def categorize_concerns(concerns):
    """Group similar concerns"""
    categories = {
        'basic_arithmetic': ['addition', 'subtraction', 'multiplication', 'division', 'math facts', 'times tables'],
        'number_sense': ['counting', 'numbers', 'quantity', 'estimation', 'magnitude'],
        'word_problems': ['word problems', 'story problems', 'reading math', 'comprehension'],
        'fractions': ['fractions', 'decimals', 'percentages', 'ratios'],
        'time': ['time', 'clock', 'telling time', 'hours', 'minutes'],
        'money': ['money', 'coins', 'currency', 'change', 'dollars'],
        'anxiety': ['anxiety', 'stress', 'fear', 'confidence', 'frustration'],
        'memory': ['memory', 'remembering', 'recall', 'forgetting'],
        'sequencing': ['sequencing', 'order', 'steps', 'procedures'],
        'spatial': ['spatial', 'visual', 'shapes', 'geometry']
    }
    
    categorized = Counter()
    for concern in concerns:
        for category, keywords in categories.items():
            if any(keyword in concern for keyword in keywords):
                categorized[category] += 1
                break
    
    return categorized

def main():
    print("Scraping dyscalculia concerns...")
    
    all_texts = []
    
    # Scrape multiple subreddits
    subreddits = [
        ('dyscalculia', 'help OR struggling OR difficulty'),
        ('teachers', 'dyscalculia OR math difficulty'),
        ('Parenting', 'dyscalculia OR math struggles'),
        ('specialed', 'dyscalculia OR math disability')
    ]
    
    for subreddit, query in subreddits:
        print(f"Scraping r/{subreddit}...")
        texts = scrape_reddit(subreddit, query, limit=50)
        all_texts.extend(texts)
    
    print(f"\nCollected {len(all_texts)} posts/comments")
    
    # Extract concerns
    concerns = extract_concerns(all_texts)
    print(f"Extracted {len(concerns)} concern mentions")
    
    # Categorize and count
    categorized = categorize_concerns(concerns)
    
    # Sort by frequency
    sorted_concerns = sorted(categorized.items(), key=lambda x: x[1], reverse=True)
    
    # Save results
    results = {
        'concerns_ranked': [{'concern': k, 'frequency': v} for k, v in sorted_concerns],
        'total_mentions': sum(categorized.values())
    }
    
    with open('concerns_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display results
    print("\n" + "="*50)
    print("DYSCALCULIA CONCERNS (Highest to Lowest)")
    print("="*50)
    for concern, count in sorted_concerns:
        print(f"{concern.replace('_', ' ').title()}: {count} mentions")
    
    print(f"\nResults saved to concerns_data.json")

if __name__ == '__main__':
    main()
