import os
import re
import sqlite3
import json
import base64
from pathlib import Path
import boto3
from datetime import datetime

class PDFProcessor:
    def __init__(self, articles_dir, aws_access_key=None, aws_secret_key=None, aws_region='us-east-1'):
        self.articles_dir = Path(articles_dir)
        self.db_path = self.articles_dir / "research_summaries.db"
        
        # Initialize AWS Bedrock
        if aws_access_key and aws_secret_key:
            self.bedrock = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        else:
            self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
        
        self.setup_database()
    
    def setup_database(self):
        """Create database for storing summaries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                title TEXT,
                authors TEXT,
                year INTEGER,
                paper_type TEXT,
                summary TEXT,
                processed_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def analyze_pdf_with_claude(self, pdf_path):
        """Analyze PDF using Claude 3.5 Sonnet via AWS Bedrock"""
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Encode PDF to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Create prompt for Claude
            prompt = """
Analyze this academic paper and extract the following information in JSON format:

1. First author's last name (for filename)
2. Publication year
3. Full title
4. All authors
5. Paper type (Research Study/Review/Meta-Analysis/Case Study/Theoretical Paper/Other)
6. A structured summary

Return ONLY valid JSON in this exact format:
{
  "author": "LastName",
  "year": "2024",
  "title": "Full Paper Title",
  "authors": "Author1, Author2, Author3",
  "paper_type": "Research Study",
  "summary": "**What this research is about:**\n[Plain English explanation]\n\n**What they did/analyzed:**\n[Methodology/approach]\n\n**Key findings/conclusions:**\n• [Point 1]\n• [Point 2]\n• [Point 3]\n\n**Why this matters for dyscalculia tools:**\n[Practical implications]\n\n**Important notes:**\n[Limitations/considerations]"
}

Make the summary easy to read and understand. Adapt the language based on paper type.
"""
            
            # Call Claude 3.5 Sonnet via Bedrock
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "temperature": 0.3,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Extract JSON from response (Claude might wrap it in markdown)
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                print(f"Could not parse JSON from Claude response")
                return None
                
        except Exception as e:
            print(f"Error analyzing PDF with Claude: {e}")
            return None
    
    def save_to_database(self, filename, title, authors, year, paper_type, summary):
        """Save paper information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO papers 
                (filename, title, authors, year, paper_type, summary, processed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (filename, title, authors, year, paper_type, summary, datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            conn.close()
    
    def process_pdf(self, pdf_path):
        """Process a single PDF: extract info, rename, and summarize"""
        print(f"Processing: {pdf_path.name}")
        
        # Analyze PDF with Claude
        result = self.analyze_pdf_with_claude(pdf_path)
        
        if not result:
            print(f"Failed to analyze {pdf_path.name}")
            return False
        
        try:
            # Extract fields from result
            author = result.get('author', '')
            year = result.get('year', '')
            title = result.get('title', '')
            authors = result.get('authors', '')
            paper_type = result.get('paper_type', '')
            summary = result.get('summary', '')
            
            # Create new filename
            if author and year:
                new_filename = f"{author}{year}.pdf"
            else:
                new_filename = pdf_path.name  # Keep original if extraction fails
            
            # Rename file if needed
            new_path = pdf_path.parent / new_filename
            if new_filename != pdf_path.name and not new_path.exists():
                pdf_path.rename(new_path)
                print(f"Renamed to: {new_filename}")
            else:
                new_filename = pdf_path.name
                print(f"Kept original name: {new_filename}")
            
            # Save to database
            self.save_to_database(new_filename, title, authors, year, paper_type, summary)
            
            print(f"✓ Processed successfully")
            return True
            
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            return False
    

    
    def process_all_pdfs(self):
        """Process all PDFs in the articles directory"""
        pdf_files = list(self.articles_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("No PDF files found in the articles directory")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        processed = 0
        for pdf_file in pdf_files:
            if self.process_pdf(pdf_file):
                processed += 1
            print("-" * 50)
        
        print(f"\nCompleted! Successfully processed {processed}/{len(pdf_files)} files")
        print(f"Database saved to: {self.db_path}")
    


if __name__ == "__main__":
    # Configuration
    articles_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    # Optional: AWS credentials (if not using default AWS profile)
    aws_access_key = None  # Replace with your AWS access key if needed
    aws_secret_key = None  # Replace with your AWS secret key if needed
    
    # Create processor and run
    processor = PDFProcessor(
        articles_dir=articles_dir,
        aws_access_key=aws_access_key,
        aws_secret_key=aws_secret_key
    )
    
    processor.process_all_pdfs()