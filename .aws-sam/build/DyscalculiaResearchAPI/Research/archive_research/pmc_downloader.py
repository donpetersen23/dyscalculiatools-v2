import requests
from pathlib import Path
import time
import re

class PMCDownloader:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def search(self, query, max_results=10):
        params = {'db': 'pmc', 'term': query, 'retmax': max_results, 'retmode': 'json'}
        response = requests.get(f"{self.base_url}esearch.fcgi", params=params)
        if response.status_code == 200:
            ids = response.json().get('esearchresult', {}).get('idlist', [])
            return self._get_details(ids)
        return []
    
    def _get_details(self, ids):
        if not ids:
            return []
        params = {'db': 'pmc', 'id': ','.join(ids), 'retmode': 'xml'}
        response = requests.get(f"{self.base_url}efetch.fcgi", params=params)
        if response.status_code == 200:
            return self._parse_xml(response.text)
        return []
    
    def _parse_xml(self, xml_text):
        results = []
        articles = re.findall(r'<article[^>]*>(.*?)</article>', xml_text, re.DOTALL)
        for article in articles:
            title_match = re.search(r'<article-title[^>]*>(.*?)</article-title>', article, re.DOTALL)
            year_match = re.search(r'<year[^>]*>(\d{4})</year>', article)
            pmcid_match = re.search(r'pub-id-type=["\']pmc["\'][^>]*>PMC(\d+)</article-id>', article)
            
            title = re.sub(r'<[^>]+>', '', title_match.group(1)) if title_match else 'No title'
            results.append({
                'title': title.strip(),
                'year': year_match.group(1) if year_match else 'Unknown',
                'url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid_match.group(1)}/" if pmcid_match else '',
                'pmcid': pmcid_match.group(1) if pmcid_match else None
            })
        return results
    
    def download_pdf(self, result, download_dir="downloads"):
        if not result.get('pmcid'):
            return None
        
        download_path = Path(download_dir)
        download_path.mkdir(exist_ok=True)
        
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{result['pmcid']}/pdf/"
        safe_title = "".join(c for c in result['title'][:40] if c.isalnum() or c in (' ', '-', '_'))
        filename = f"PMC_{safe_title}.pdf"
        
        try:
            time.sleep(1)
            response = requests.get(pdf_url, headers=self.headers, timeout=30)
            if response.status_code == 200 and 'pdf' in response.headers.get('content-type', ''):
                with open(download_path / filename, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            print(f"Failed: {e}")
        return None
