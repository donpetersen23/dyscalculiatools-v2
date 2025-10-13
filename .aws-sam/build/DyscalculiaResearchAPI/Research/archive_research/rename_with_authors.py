import os
import re
import requests
from xml.etree import ElementTree as ET

class AuthorRenamer:
    def __init__(self, articles_dir):
        self.articles_dir = articles_dir
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def get_article_metadata(self, pmc_id):
        """Get article metadata including authors"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pmc',
            'id': pmc_id,
            'retmode': 'xml'
        }
        
        try:
            response = requests.get(fetch_url, params=params)
            root = ET.fromstring(response.content)
            
            # Extract first author's last name
            authors = root.findall('.//contrib[@contrib-type="author"]//surname')
            if authors:
                first_author = authors[0].text
                return first_author
            
            # Fallback: try different XML structure
            authors = root.findall('.//name/surname')
            if authors:
                return authors[0].text
                
        except Exception as e:
            print(f"Error fetching metadata for PMC{pmc_id}: {e}")
        
        return None
    
    def sanitize_filename(self, name):
        """Remove invalid filename characters"""
        return re.sub(r'[<>:"/\\|?*]', '', name)
    
    def rename_files(self):
        """Rename all PMC files to include author names"""
        pmc_files = [f for f in os.listdir(self.articles_dir) if f.startswith('PMC') and f.endswith('.pdf')]
        
        for filename in pmc_files:
            # Extract PMC ID
            pmc_match = re.match(r'PMC(\d+)\.pdf', filename)
            if not pmc_match:
                continue
                
            pmc_id = pmc_match.group(1)
            old_path = os.path.join(self.articles_dir, filename)
            
            # Get author
            author = self.get_article_metadata(pmc_id)
            if author:
                author = self.sanitize_filename(author)
                new_filename = f"{author}_PMC{pmc_id}.pdf"
                new_path = os.path.join(self.articles_dir, new_filename)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Error renaming {filename}: {e}")
            else:
                print(f"No author found for {filename}")

if __name__ == "__main__":
    articles_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    renamer = AuthorRenamer(articles_dir)
    renamer.rename_files()