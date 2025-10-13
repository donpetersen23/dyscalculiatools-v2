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
            print(f"ERIC status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                results = self._format_eric_results(data)
                print(f"ERIC results count: {len(results)}")
                return results
            else:
                print(f"ERIC error: Status {response.status_code}")
        except Exception as e:
            print(f"ERIC exception: {e}")
            return []
        
        return []
    
    def search_pubmed_central(self, query, max_results=10):
        """Search PubMed Central for medical/psychology research"""
        search_params = {
            'db': 'pmc',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        try:
            search_response = requests.get(f"{self.pubmed_base_url}esearch.fcgi", params=search_params)
            print(f"PMC status: {search_response.status_code}")
            print(f"PMC search URL: {search_response.url}")
            if search_response.status_code == 200:
                search_data = search_response.json()
                print(f"PMC search response: {search_data}")
                ids = search_data.get('esearchresult', {}).get('idlist', [])
                print(f"PMC IDs found: {len(ids)} - {ids}")
                
                if ids:
                    return self._get_pmc_details(ids)
        except Exception as e:
            print(f"PMC exception: {e}")
            return []
        
        return []
    
    def search_google_scholar(self, query, max_results=10):
        """Search Google Scholar for academic papers"""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.scholar_base_url}?q={encoded_query}&num={max_results}"
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers)
            print(f"Scholar status: {response.status_code}")
            if response.status_code == 200:
                results = self._parse_scholar_results(response.text)
                print(f"Scholar results count: {len(results)}")
                return results
            else:
                print(f"Scholar error: Status {response.status_code}")
        except Exception as e:
            print(f"Scholar exception: {e}")
            return []
        
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
    
    def _get_pmc_details(self, ids):
        """Get detailed information for PMC articles"""
        id_string = ','.join(ids)
        detail_params = {
            'db': 'pmc',
            'id': id_string,
            'retmode': 'xml'
        }
        
        try:
            detail_response = requests.get(f"{self.pubmed_base_url}efetch.fcgi", params=detail_params)
            print(f"PMC fetch status: {detail_response.status_code}")
            print(f"PMC fetch URL: {detail_response.url}")
            if detail_response.status_code == 200:
                print(f"PMC XML response length: {len(detail_response.text)}")
                print(f"PMC XML first 500 chars: {detail_response.text[:500]}")
                return self._parse_pmc_xml(detail_response.text)
        except Exception as e:
            print(f"PMC details error: {e}")
            return []
        
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
    
    def _parse_pmc_xml(self, xml_text):
        """Parse PMC XML with proper handling of namespaces and structure"""
        results = []
        # Match articles with any attributes
        articles = re.findall(r'<article[^>]*>(.*?)</article>', xml_text, re.DOTALL)
        print(f"PMC articles found: {len(articles)}")
        
        for i, article in enumerate(articles):
            # Extract title from article-title tag
            title_match = re.search(r'<article-title[^>]*>(.*?)</article-title>', article, re.DOTALL)
            # Extract abstract text, handling nested tags
            abstract_match = re.search(r'<abstract[^>]*>(.*?)</abstract>', article, re.DOTALL)
            # Extract year from pub-date
            year_match = re.search(r'<pub-date[^>]*>.*?<year[^>]*>(\d{4})</year>', article, re.DOTALL)
            # Extract PMC ID
            pmcid_match = re.search(r'<article-id[^>]*pub-id-type=["\']pmc["\'][^>]*>PMC(\d+)</article-id>', article)
            
            # Clean up title and abstract by removing HTML tags
            title = re.sub(r'<[^>]+>', '', title_match.group(1)) if title_match else 'No title'
            abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)) if abstract_match else 'No abstract'
            
            result = {
                'database': 'PubMed Central',
                'title': title.strip(),
                'authors': 'Authors not parsed',
                'year': year_match.group(1) if year_match else 'Unknown',
                'abstract': abstract.strip()[:500] + '...' if len(abstract.strip()) > 500 else abstract.strip(),
                'url': f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid_match.group(1)}/" if pmcid_match else ''
            }
            results.append(result)
            print(f"PMC article {i+1}: {result['title'][:50]}...")
        
        return results
    
    def get_real_studies(self, intervention_name):
        """Get real studies for the web interface"""
        eric_query = f"dyscalculia AND {intervention_name}"
        pmc_query = f"dyscalculia {intervention_name}"
        scholar_query = f"dyscalculia {intervention_name}"
        
        eric_results = self.search_eric(eric_query, 2)
        pmc_results = self.search_pubmed_central(pmc_query, 2)
        scholar_results = self.search_google_scholar(scholar_query, 1)
        
        all_results = []
        if isinstance(eric_results, list):
            all_results.extend(eric_results)
        if isinstance(pmc_results, list):
            all_results.extend(pmc_results)
        if isinstance(scholar_results, list):
            all_results.extend(scholar_results)
        
        return all_results[:5]
    
    def download_pdfs(self, results, download_dir="downloads"):
        """Download PDFs for research results"""
        from pathlib import Path
        import os
        
        download_path = Path(download_dir)
        download_path.mkdir(exist_ok=True)
        
        downloaded = []
        for i, result in enumerate(results):
            if 'url' in result and result['url']:
                # Generate PDF URL for PMC articles
                if 'pmc/articles/PMC' in result['url']:
                    pdf_url = result['url'].replace('/pmc/articles/', '/pmc/articles/') + 'pdf/'
                else:
                    pdf_url = result['url']
                
                # Create safe filename
                title = result.get('title', 'Unknown')[:40]
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{i+1:02d}_{result['database']}_{safe_title}.pdf"
                
                try:
                    import time
                    time.sleep(1)
                    response = requests.get(pdf_url, headers=self.headers, timeout=30)
                    if response.status_code == 200 and 'pdf' in response.headers.get('content-type', ''):
                        filepath = download_path / filename
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        downloaded.append({'title': result['title'], 'file': filename})
                        print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Failed to download {result['title']}: {e}")
        
        return downloaded