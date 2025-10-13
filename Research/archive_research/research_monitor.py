import os
import json
import sqlite3
from datetime import datetime, timedelta
import requests
from xml.etree import ElementTree as ET

class ResearchMonitor:
    def __init__(self, db_path="research_monitor.db"):
        self.db_path = db_path
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for tracking papers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                pmid TEXT PRIMARY KEY,
                pmc_id TEXT,
                title TEXT,
                authors TEXT,
                abstract TEXT,
                publication_date TEXT,
                journal TEXT,
                doi TEXT,
                keywords TEXT,
                first_seen DATE,
                pdf_available BOOLEAN,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date DATE,
                query TEXT,
                new_papers_found INTEGER,
                total_papers INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_last_check_date(self):
        """Get the last monitoring check date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(check_date) FROM monitoring_log')
        result = cursor.fetchone()[0]
        conn.close()
        
        if result:
            return datetime.strptime(result, '%Y-%m-%d').date()
        else:
            # If no previous check, start from 30 days ago
            return (datetime.now() - timedelta(days=30)).date()
    
    def search_new_papers(self, query, days_back=7):
        """Search for papers published in the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for PubMed query
        date_query = f'("{start_date.strftime("%Y/%m/%d")}"[Date - Publication] : "{end_date.strftime("%Y/%m/%d")}"[Date - Publication])'
        full_query = f"{query} AND {date_query}"
        
        print(f"Searching for: {full_query}")
        
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': full_query,
            'retmax': 100,
            'retmode': 'xml'
        }
        
        response = requests.get(search_url, params=params, headers=self.headers)
        root = ET.fromstring(response.content)
        
        pmids = [id_elem.text for id_elem in root.findall('.//Id')]
        print(f"Found {len(pmids)} new papers")
        return pmids
    
    def get_paper_details(self, pmids):
        """Fetch detailed information for papers"""
        if not pmids:
            return []
        
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }
        
        response = requests.get(fetch_url, params=params, headers=self.headers)
        root = ET.fromstring(response.content)
        
        papers = []
        for article in root.findall('.//PubmedArticle'):
            paper_data = self.extract_paper_data(article)
            if paper_data:
                papers.append(paper_data)
        
        return papers
    
    def extract_paper_data(self, article):
        """Extract relevant data from PubMed XML"""
        try:
            # Basic info
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No Title"
            
            # Authors
            authors = []
            for author in article.findall('.//Author'):
                lastname = author.find('.//LastName')
                forename = author.find('.//ForeName')
                if lastname is not None:
                    name = lastname.text
                    if forename is not None:
                        name = f"{forename.text} {name}"
                    authors.append(name)
            
            # Abstract
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Publication date
            pub_date = self.extract_publication_date(article)
            
            # Journal
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ""
            
            # DOI
            doi_elem = article.find('.//ELocationID[@EIdType="doi"]')
            doi = doi_elem.text if doi_elem is not None else ""
            
            # Keywords
            keywords = []
            for keyword in article.findall('.//Keyword'):
                if keyword.text:
                    keywords.append(keyword.text)
            
            return {
                'pmid': pmid,
                'title': title,
                'authors': '; '.join(authors),
                'abstract': abstract,
                'publication_date': pub_date,
                'journal': journal,
                'doi': doi,
                'keywords': '; '.join(keywords),
                'first_seen': datetime.now().date().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting paper data: {e}")
            return None
    
    def extract_publication_date(self, article):
        """Extract publication date from article XML"""
        pub_date = article.find('.//PubDate')
        if pub_date is not None:
            year = pub_date.find('.//Year')
            month = pub_date.find('.//Month')
            day = pub_date.find('.//Day')
            
            if year is not None:
                date_str = year.text
                if month is not None:
                    date_str += f"-{month.text.zfill(2)}"
                    if day is not None:
                        date_str += f"-{day.text.zfill(2)}"
                return date_str
        return ""
    
    def save_papers(self, papers):
        """Save new papers to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_count = 0
        for paper in papers:
            cursor.execute('SELECT pmid FROM papers WHERE pmid = ?', (paper['pmid'],))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO papers 
                    (pmid, title, authors, abstract, publication_date, journal, doi, keywords, first_seen, pdf_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paper['pmid'], paper['title'], paper['authors'], paper['abstract'],
                    paper['publication_date'], paper['journal'], paper['doi'], 
                    paper['keywords'], paper['first_seen'], False
                ))
                new_count += 1
        
        conn.commit()
        conn.close()
        return new_count
    
    def log_monitoring_session(self, query, new_papers, total_papers):
        """Log the monitoring session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitoring_log (check_date, query, new_papers_found, total_papers)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().date().isoformat(), query, new_papers, total_papers))
        
        conn.commit()
        conn.close()
    
    def monitor_research(self, queries, days_back=7):
        """Main monitoring function"""
        print(f"Starting research monitoring - checking last {days_back} days")
        
        total_new = 0
        for query in queries:
            print(f"\n--- Monitoring: {query} ---")
            
            # Search for new papers
            pmids = self.search_new_papers(query, days_back)
            
            if pmids:
                # Get detailed information
                papers = self.get_paper_details(pmids)
                
                # Save to database
                new_count = self.save_papers(papers)
                total_new += new_count
                
                print(f"Added {new_count} new papers to database")
                
                # Log this session
                self.log_monitoring_session(query, new_count, len(pmids))
            else:
                print("No new papers found")
                self.log_monitoring_session(query, 0, 0)
        
        print(f"\n=== Monitoring Complete ===")
        print(f"Total new papers added: {total_new}")
        return total_new
    
    def get_recent_papers(self, days=30, limit=10):
        """Get recently added papers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, authors, publication_date, journal, abstract
            FROM papers 
            WHERE first_seen >= date('now', '-{} days')
            ORDER BY first_seen DESC
            LIMIT ?
        '''.format(days), (limit,))
        
        papers = cursor.fetchall()
        conn.close()
        return papers
    
    def get_monitoring_stats(self):
        """Get monitoring statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total papers
        cursor.execute('SELECT COUNT(*) FROM papers')
        total_papers = cursor.fetchone()[0]
        
        # Papers added in last 30 days
        cursor.execute('''
            SELECT COUNT(*) FROM papers 
            WHERE first_seen >= date('now', '-30 days')
        ''')
        recent_papers = cursor.fetchone()[0]
        
        # Last monitoring session
        cursor.execute('''
            SELECT check_date, SUM(new_papers_found) 
            FROM monitoring_log 
            WHERE check_date = (SELECT MAX(check_date) FROM monitoring_log)
        ''')
        last_session = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_papers': total_papers,
            'recent_papers': recent_papers,
            'last_check': last_session[0] if last_session[0] else 'Never',
            'last_session_new': last_session[1] if last_session[1] else 0
        }

if __name__ == "__main__":
    # Configuration
    queries = [
        "dyscalculia",
        "mathematical learning disability", 
        "numerical cognition disorder",
        "math anxiety",
        "number sense deficit"
    ]
    
    monitor = ResearchMonitor()
    
    # Run monitoring (check last 7 days)
    monitor.monitor_research(queries, days_back=7)
    
    # Show stats
    stats = monitor.get_monitoring_stats()
    print(f"\n=== Database Stats ===")
    print(f"Total papers tracked: {stats['total_papers']}")
    print(f"Papers added in last 30 days: {stats['recent_papers']}")
    print(f"Last check: {stats['last_check']}")
    print(f"New papers in last session: {stats['last_session_new']}")