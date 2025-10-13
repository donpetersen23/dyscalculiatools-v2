import os
import time
import requests
from xml.etree import ElementTree as ET
from PyPDF2 import PdfReader

class PubMedDownloader:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def search_articles(self, query, max_results=100):
        """Search PubMed Central for articles"""
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pmc',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml'
        }
        response = requests.get(search_url, params=params, headers=self.headers)
        root = ET.fromstring(response.content)
        ids = [id_elem.text for id_elem in root.findall('.//Id')]
        print(f"Found {len(ids)} articles")
        return ids
    
    def get_article_details(self, pmc_id):
        """Get article metadata including title and authors"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pmc',
            'id': pmc_id,
            'retmode': 'xml'
        }
        try:
            response = requests.get(fetch_url, params=params, headers=self.headers)
            root = ET.fromstring(response.content)
            
            # Extract title
            title_elem = root.find('.//article-title')
            title = title_elem.text if title_elem is not None else "Unknown Title"
            
            # Extract authors
            authors = []
            for contrib in root.findall('.//contrib[@contrib-type="author"]'):
                surname = contrib.find('.//surname')
                given_names = contrib.find('.//given-names')
                if surname is not None:
                    author = surname.text
                    if given_names is not None:
                        author = f"{given_names.text} {author}"
                    authors.append(author)
            
            return title, authors
        except Exception as e:
            print(f"Error fetching details for PMC{pmc_id}: {e}")
            return "Unknown Title", []
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename[:100]  # Limit length
    
    def get_pdf_url(self, pmc_id):
        """Get PDF download URL for a PMC article"""
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/PMC{pmc_id}.pdf"
    
    def download_pdf(self, pmc_id):
        """Download PDF if not already exists"""
        filename = f"PMC{pmc_id}.pdf"
        filepath = os.path.join(self.download_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Skipping PMC{pmc_id} - already downloaded")
            return False
        
        pdf_url = self.get_pdf_url(pmc_id)
        try:
            response = requests.get(pdf_url, timeout=30, allow_redirects=True, headers=self.headers)
            print(f"PMC{pmc_id}: Status {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' in content_type:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    if self.validate_pdf(filepath):
                        print(f"Downloaded PMC{pmc_id}")
                        return True
                    else:
                        os.remove(filepath)
                        print(f"Invalid PDF for PMC{pmc_id}")
                        return False
                else:
                    # Try alternative URL formats
                    alt_urls = [
                        f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/PMC{pmc_id}.pdf",
                        f"https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_pdf/{pmc_id[:2]}/{pmc_id[2:4]}/PMC{pmc_id}.tar.gz",
                        f"https://europepmc.org/articles/PMC{pmc_id}?pdf=render"
                    ]
                    
                    for alt_url in alt_urls:
                        try:
                            alt_response = requests.get(alt_url, timeout=30, allow_redirects=True, headers=self.headers)
                            if alt_response.status_code == 200 and 'application/pdf' in alt_response.headers.get('Content-Type', ''):
                                with open(filepath, 'wb') as f:
                                    f.write(alt_response.content)
                                if self.validate_pdf(filepath):
                                    print(f"Downloaded PMC{pmc_id} (alternative URL)")
                                    return True
                                else:
                                    os.remove(filepath)
                        except:
                            continue
                    
                    print(f"No PDF available for PMC{pmc_id} (Content-Type: {content_type})")
                    return False
            else:
                print(f"No PDF available for PMC{pmc_id} (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"Error downloading PMC{pmc_id}: {e}")
            return False
    
    def validate_pdf(self, filepath):
        """Validate that the downloaded file is a proper PDF"""
        try:
            PdfReader(filepath)
            return True
        except:
            return False
    
    def download_all(self, query, max_results=100, delay=1):
        """Search and download all articles for a query"""
        print(f"Searching for: {query}")
        pmc_ids = self.search_articles(query, max_results)
        
        downloaded = 0
        for pmc_id in pmc_ids:
            if self.download_pdf(pmc_id):
                downloaded += 1
            time.sleep(delay)
        
        print(f"\nCompleted! Downloaded {downloaded} new articles")

if __name__ == "__main__":
    download_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    downloader = PubMedDownloader(download_dir)
    
    queries = [
        "dyscalculia",
        "mathematical learning disability",
        "numerical cognition disorder"
    ]
    
    for query in queries:
        downloader.download_all(query, max_results=50, delay=1)
        print("\n" + "="*50 + "\n")
