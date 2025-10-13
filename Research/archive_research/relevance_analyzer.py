import os
import requests
import re
from xml.etree import ElementTree as ET
import csv

class DyscalculiaRelevanceAnalyzer:
    def __init__(self, articles_dir):
        self.articles_dir = articles_dir
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_pmc_ids_from_files(self):
        """Extract PMC IDs from downloaded PDF filenames"""
        pmc_ids = []
        for filename in os.listdir(self.articles_dir):
            if filename.startswith('PMC') and filename.endswith('.pdf'):
                pmc_id = filename.replace('PMC', '').replace('.pdf', '')
                pmc_ids.append(pmc_id)
        return pmc_ids
    
    def get_article_metadata(self, pmc_id):
        """Get title and abstract for a PMC article"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pmc',
            'id': pmc_id,
            'retmode': 'xml'
        }
        
        try:
            response = requests.get(fetch_url, params=params, headers=self.headers, timeout=10)
            root = ET.fromstring(response.content)
            
            # Extract title
            title_elem = root.find('.//article-title')
            title = title_elem.text if title_elem is not None else ""
            
            # Extract abstract
            abstract_elem = root.find('.//abstract')
            abstract = ""
            if abstract_elem is not None:
                abstract = ' '.join([p.text or '' for p in abstract_elem.findall('.//p')])
            
            return title, abstract
        except Exception as e:
            print(f"Error fetching PMC{pmc_id}: {e}")
            return "", ""
    
    def calculate_relevance_score(self, title, abstract):
        """Calculate relevance score for dyscalculia research (0-100)"""
        text = (title + " " + abstract).lower()
        
        # High relevance keywords
        high_keywords = ['dyscalculia', 'mathematical learning disability', 'number processing disorder']
        medium_keywords = ['mathematical difficulties', 'numerical cognition', 'math anxiety', 'arithmetic skills', 
                          'number sense', 'mathematical ability', 'numerical processing', 'math learning']
        low_keywords = ['mathematics', 'numerical', 'arithmetic', 'calculation', 'math', 'cognitive']
        
        score = 0
        
        # High relevance (30 points each)
        for keyword in high_keywords:
            if keyword in text:
                score += 30
        
        # Medium relevance (15 points each)
        for keyword in medium_keywords:
            if keyword in text:
                score += 15
        
        # Low relevance (5 points each)
        for keyword in low_keywords:
            if keyword in text:
                score += 5
        
        # Cap at 100
        return min(score, 100)
    
    def analyze_all_articles(self):
        """Analyze all downloaded articles and return relevance scores"""
        pmc_ids = self.get_pmc_ids_from_files()
        results = []
        
        print(f"Analyzing {len(pmc_ids)} articles for dyscalculia relevance...")
        
        for i, pmc_id in enumerate(pmc_ids, 1):
            print(f"Processing PMC{pmc_id} ({i}/{len(pmc_ids)})")
            
            title, abstract = self.get_article_metadata(pmc_id)
            score = self.calculate_relevance_score(title, abstract)
            
            results.append({
                'PMC_ID': f'PMC{pmc_id}',
                'Title': title[:100] + '...' if len(title) > 100 else title,
                'Relevance_Score': score,
                'Abstract_Preview': abstract[:200] + '...' if len(abstract) > 200 else abstract
            })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['Relevance_Score'], reverse=True)
        return results
    
    def save_results(self, results, output_file):
        """Save results to CSV file"""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['PMC_ID', 'Title', 'Relevance_Score', 'Abstract_Preview'])
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {output_file}")

if __name__ == "__main__":
    articles_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    output_file = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\dyscalculia_relevance_scores.csv"
    
    analyzer = DyscalculiaRelevanceAnalyzer(articles_dir)
    results = analyzer.analyze_all_articles()
    
    # Display top 10 most relevant
    print("\n" + "="*80)
    print("TOP 10 MOST RELEVANT ARTICLES FOR DYSCALCULIA RESEARCH:")
    print("="*80)
    
    for i, article in enumerate(results[:10], 1):
        print(f"{i}. {article['PMC_ID']} (Score: {article['Relevance_Score']})")
        print(f"   Title: {article['Title']}")
        print()
    
    analyzer.save_results(results, output_file)