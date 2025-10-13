import requests
from pathlib import Path
import time

class ERICDownloader:
    def __init__(self):
        self.base_url = "https://api.ies.ed.gov/eric/"
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def search(self, query, max_results=10):
        params = {'search': query, 'format': 'json', 'rows': max_results}
        response = requests.get(f"{self.base_url}search", params=params)
        if response.status_code == 200:
            return self._format_results(response.json())
        return []
    
    def _format_results(self, data):
        results = []
        for doc in data.get('response', {}).get('docs', []):
            results.append({
                'title': doc.get('title', ['No title'])[0],
                'authors': ', '.join(doc.get('author', [])),
                'year': doc.get('publicationdateyear', ['Unknown'])[0],
                'abstract': doc.get('description', ['No abstract'])[0],
                'url': f"https://eric.ed.gov/?id={doc.get('id', '')}"
            })
        return results
    
    def download_pdf(self, result, download_dir="downloads"):
        download_path = Path(download_dir)
        download_path.mkdir(exist_ok=True)
        
        safe_title = "".join(c for c in result['title'][:40] if c.isalnum() or c in (' ', '-', '_'))
        filename = f"ERIC_{safe_title}.pdf"
        
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
