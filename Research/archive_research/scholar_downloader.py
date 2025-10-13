import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re

class ScholarDownloader:
    def __init__(self):
        self.base_url = "https://scholar.google.com/scholar"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def search(self, query, max_results=10):
        import urllib.parse
        url = f"{self.base_url}?q={urllib.parse.quote(query)}&num={max_results}"
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return self._parse_results(response.text)
        except Exception as e:
            print(f"Error: {e}")
        return []
    
    def _parse_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for result in soup.find_all('div', class_='gs_r gs_or gs_scl'):
            try:
                title_elem = result.find('h3', class_='gs_rt')
                title = title_elem.get_text() if title_elem else 'No title'
                link_elem = title_elem.find('a') if title_elem else None
                url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ''
                
                authors_elem = result.find('div', class_='gs_a')
                authors = authors_elem.get_text() if authors_elem else 'Unknown'
                year_match = re.search(r'(19|20)\d{2}', authors)
                
                results.append({
                    'title': title.strip(),
                    'authors': authors.strip(),
                    'year': year_match.group() if year_match else 'Unknown',
                    'url': url
                })
            except:
                continue
        return results
    
    def download_pdf(self, result, download_dir="downloads"):
        if not result.get('url'):
            return None
        
        download_path = Path(download_dir)
        download_path.mkdir(exist_ok=True)
        
        safe_title = "".join(c for c in result['title'][:40] if c.isalnum() or c in (' ', '-', '_'))
        filename = f"Scholar_{safe_title}.pdf"
        
        try:
            time.sleep(1)
            response = requests.get(result['url'], headers=self.headers, timeout=30)
            if response.status_code == 200 and 'pdf' in response.headers.get('content-type', ''):
                with open(download_path / filename, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            print(f"Failed: {e}")
        return None
