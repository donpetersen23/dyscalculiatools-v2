import os
import PyPDF2
import pandas as pd
from collections import Counter
import re
from datetime import datetime
import json

class PDFAnalyzer:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.results = []
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def extract_key_sections(self, text):
        """Extract key sections like abstract, conclusions, results"""
        sections = {}
        
        # Common section patterns
        patterns = {
            'abstract': r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*(?:introduction|keywords|background|\d+\.|references))',
            'conclusions': r'(?i)(?:conclusions?|discussion|summary)\s*:?\s*(.*?)(?=\n\s*(?:references|acknowledgments|funding|\d+\.))',
            'results': r'(?i)results\s*:?\s*(.*?)(?=\n\s*(?:discussion|conclusions?|references|\d+\.))',
            'methods': r'(?i)(?:methods?|methodology)\s*:?\s*(.*?)(?=\n\s*(?:results|discussion|\d+\.))'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()[:1000]  # Limit to 1000 chars
        
        return sections
    
    def extract_key_findings(self, text):
        """Extract key findings and insights"""
        findings = []
        
        # Look for sentences with key indicator words
        key_indicators = [
            r'(?i)we found that',
            r'(?i)results show',
            r'(?i)significantly',
            r'(?i)our findings',
            r'(?i)demonstrated that',
            r'(?i)evidence suggests',
            r'(?i)concluded that',
            r'(?i)indicates that',
            r'(?i)revealed that'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50 and len(sentence) < 300:  # Reasonable length
                for indicator in key_indicators:
                    if re.search(indicator, sentence):
                        findings.append(sentence)
                        break
        
        return findings[:10]  # Top 10 findings
    
    def extract_keywords(self, text):
        """Extract relevant keywords and terms"""
        # Common research keywords related to dyscalculia and learning disabilities
        domain_keywords = [
            'dyscalculia', 'mathematical', 'numerical', 'arithmetic', 'cognition',
            'learning disability', 'intervention', 'assessment', 'diagnosis',
            'working memory', 'number sense', 'calculation', 'mathematics',
            'cognitive', 'neurological', 'brain', 'development', 'children',
            'students', 'education', 'therapy', 'treatment', 'remediation'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in domain_keywords:
            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
            if count > 0:
                found_keywords.append((keyword, count))
        
        return sorted(found_keywords, key=lambda x: x[1], reverse=True)[:15]
    
    def analyze_single_pdf(self, pdf_path):
        """Analyze a single PDF and extract insights"""
        filename = os.path.basename(pdf_path)
        print(f"Analyzing: {filename}")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        sections = self.extract_key_sections(text)
        findings = self.extract_key_findings(text)
        keywords = self.extract_keywords(text)
        
        # Calculate relevance score based on keyword frequency
        relevance_score = sum(count for _, count in keywords)
        
        analysis = {
            'filename': filename,
            'file_path': pdf_path,
            'word_count': len(text.split()),
            'relevance_score': relevance_score,
            'sections': sections,
            'key_findings': findings,
            'keywords': keywords,
            'analysis_date': datetime.now().isoformat()
        }
        
        return analysis
    
    def analyze_all_pdfs(self, max_files=None):
        """Analyze all PDFs in the directory"""
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.lower().endswith('.pdf')]
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        print(f"Found {len(pdf_files)} PDF files to analyze")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            analysis = self.analyze_single_pdf(pdf_path)
            if analysis:
                self.results.append(analysis)
        
        return self.results
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        if not self.results:
            return "No analysis results available"
        
        # Sort by relevance score
        sorted_results = sorted(self.results, key=lambda x: x['relevance_score'], reverse=True)
        
        report = []
        report.append("=" * 80)
        report.append("PDF ANALYSIS SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Total PDFs Analyzed: {len(self.results)}")
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Top insights from highest relevance papers
        report.append("TOP 10 MOST RELEVANT PAPERS:")
        report.append("-" * 40)
        
        for i, result in enumerate(sorted_results[:10], 1):
            report.append(f"{i}. {result['filename']}")
            report.append(f"   Relevance Score: {result['relevance_score']}")
            report.append(f"   Word Count: {result['word_count']}")
            
            # Show top keywords
            if result['keywords']:
                top_keywords = [kw[0] for kw in result['keywords'][:5]]
                report.append(f"   Key Terms: {', '.join(top_keywords)}")
            
            # Show key findings
            if result['key_findings']:
                report.append("   Key Finding:")
                report.append(f"   → {result['key_findings'][0][:200]}...")
            
            report.append("")
        
        # Overall keyword analysis
        all_keywords = {}
        for result in self.results:
            for keyword, count in result['keywords']:
                all_keywords[keyword] = all_keywords.get(keyword, 0) + count
        
        report.append("MOST FREQUENT RESEARCH TERMS:")
        report.append("-" * 40)
        top_terms = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:15]
        for term, count in top_terms:
            report.append(f"{term}: {count} occurrences")
        
        report.append("")
        
        # Key insights compilation
        report.append("STRONGEST INSIGHTS ACROSS ALL PAPERS:")
        report.append("-" * 40)
        
        all_findings = []
        for result in sorted_results[:20]:  # Top 20 papers
            all_findings.extend(result['key_findings'])
        
        # Show top findings
        for i, finding in enumerate(all_findings[:15], 1):
            report.append(f"{i}. {finding}")
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, output_file="pdf_analysis_results.json"):
        """Save analysis results to JSON file"""
        output_path = os.path.join(self.pdf_directory, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")
    
    def create_csv_summary(self, output_file="pdf_summary.csv"):
        """Create a CSV summary of all analyses"""
        if not self.results:
            return
        
        csv_data = []
        for result in self.results:
            row = {
                'filename': result['filename'],
                'relevance_score': result['relevance_score'],
                'word_count': result['word_count'],
                'top_keywords': ', '.join([kw[0] for kw in result['keywords'][:5]]),
                'has_abstract': 'abstract' in result['sections'],
                'has_conclusions': 'conclusions' in result['sections'],
                'key_findings_count': len(result['key_findings'])
            }
            csv_data.append(row)
        
        df = pd.DataFrame(csv_data)
        output_path = os.path.join(self.pdf_directory, output_file)
        df.to_csv(output_path, index=False)
        print(f"CSV summary saved to: {output_path}")

if __name__ == "__main__":
    # Analyze PDFs in the articles directory
    articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    analyzer = PDFAnalyzer(articles_dir)
    
    print("Starting PDF analysis...")
    results = analyzer.analyze_all_pdfs(max_files=20)  # Analyze first 20 files for speed
    
    print("\nGenerating summary report...")
    report = analyzer.generate_summary_report()
    print(report)
    
    # Save results
    analyzer.save_results()
    analyzer.create_csv_summary()
    
    print("\nAnalysis complete!")