import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import re

class DyscalculiaResearchAssistant:
    def __init__(self):
        self.eric_base_url = "https://api.ies.ed.gov/eric/"
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.scholar_base_url = "https://scholar.google.com/scholar"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_eric(self, query, max_results=10):
        """Search ERIC database for education research"""
        params = {
            'search': query,
            'format': 'json',
            'rows': max_results
        }
        
        try:
            response = requests.get(f"{self.eric_base_url}search", params=params)
            if response.status_code == 200:
                data = response.json()
                return self._format_eric_results(data)
        except Exception as e:
            return f"ERIC search error: {e}"
        
        return []
    
    def search_pubmed(self, query, max_results=10):
        """Search PubMed for medical/psychology research"""
        # First, search for IDs
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        try:
            search_response = requests.get(f"{self.pubmed_base_url}esearch.fcgi", params=search_params)
            if search_response.status_code == 200:
                search_data = search_response.json()
                ids = search_data.get('esearchresult', {}).get('idlist', [])
                
                if ids:
                    return self._get_pubmed_details(ids)
        except Exception as e:
            return f"PubMed search error: {e}"
        
        return []
    
    def search_google_scholar(self, query, max_results=10):
        """Search Google Scholar for academic papers"""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.scholar_base_url}?q={encoded_query}&num={max_results}"
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return self._parse_scholar_results(response.text)
        except Exception as e:
            return f"Google Scholar search error: {e}"
        
        return []
    
    def _parse_scholar_results(self, html):
        """Parse Google Scholar search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='gs_r gs_or gs_scl'):
            try:
                title_elem = result.find('h3', class_='gs_rt')
                title = title_elem.get_text() if title_elem else 'No title'
                
                link_elem = title_elem.find('a') if title_elem else None
                url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
                
                authors_elem = result.find('div', class_='gs_a')
                authors = authors_elem.get_text() if authors_elem else 'Unknown authors'
                
                snippet_elem = result.find('div', class_='gs_rs')
                abstract = snippet_elem.get_text() if snippet_elem else 'No abstract available'
                
                # Extract year from authors string
                year = 'Unknown'
                year_match = re.search(r'(19|20)\d{2}', authors)
                if year_match:
                    year = year_match.group()
                
                result_data = {
                    'database': 'Google Scholar',
                    'title': title.strip(),
                    'authors': authors.strip(),
                    'year': year,
                    'abstract': abstract.strip(),
                    'url': url
                }
                results.append(result_data)
            except Exception as e:
                continue
        
        return results
    
    def _get_pubmed_details(self, ids):
        """Get detailed information for PubMed articles"""
        id_string = ','.join(ids)
        detail_params = {
            'db': 'pubmed',
            'id': id_string,
            'retmode': 'xml'
        }
        
        try:
            detail_response = requests.get(f"{self.pubmed_base_url}efetch.fcgi", params=detail_params)
            if detail_response.status_code == 200:
                return self._parse_pubmed_xml(detail_response.text)
        except Exception as e:
            return f"PubMed details error: {e}"
        
        return []
    
    def _format_eric_results(self, data):
        """Format ERIC search results"""
        results = []
        docs = data.get('response', {}).get('docs', [])
        
        for doc in docs:
            result = {
                'database': 'ERIC',
                'title': doc.get('title', ['No title'])[0],
                'authors': ', '.join(doc.get('author', [])),
                'year': doc.get('publicationdateyear', ['Unknown'])[0],
                'abstract': doc.get('description', ['No abstract available'])[0],
                'url': f"https://eric.ed.gov/?id={doc.get('id', '')}"
            }
            results.append(result)
        
        return results
    
    def _parse_pubmed_xml(self, xml_text):
        """Basic XML parsing for PubMed results"""
        # Simple regex-based parsing for prototype
        
        results = []
        articles = re.findall(r'<PubmedArticle>(.*?)</PubmedArticle>', xml_text, re.DOTALL)
        
        for article in articles:
            title_match = re.search(r'<ArticleTitle>(.*?)</ArticleTitle>', article)
            abstract_match = re.search(r'<AbstractText>(.*?)</AbstractText>', article)
            year_match = re.search(r'<Year>(\d{4})</Year>', article)
            pmid_match = re.search(r'<PMID.*?>(.*?)</PMID>', article)
            
            result = {
                'database': 'PubMed',
                'title': title_match.group(1) if title_match else 'No title',
                'authors': 'Authors not parsed',
                'year': year_match.group(1) if year_match else 'Unknown',
                'abstract': abstract_match.group(1) if abstract_match else 'No abstract',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid_match.group(1)}/" if pmid_match else ''
            }
            results.append(result)
        
        return results
    
    def get_real_studies(self, intervention_name):
        """Get real studies for the web interface"""
        eric_query = f"dyscalculia AND {intervention_name}"
        scholar_query = f"dyscalculia {intervention_name}"
        
        eric_results = self.search_eric(eric_query, 2)
        scholar_results = self.search_google_scholar(scholar_query, 3)
        
        all_results = []
        if isinstance(eric_results, list):
            all_results.extend(eric_results)
        if isinstance(scholar_results, list):
            all_results.extend(scholar_results)
        
        return all_results[:5]