import os
import re
import json
from PyPDF2 import PdfReader
from pathlib import Path

class TextExtractor:
    def __init__(self, pdf_dir, output_dir):
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a single PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def clean_text(self, text):
        """Clean and preprocess extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\n\d+\n', '\n', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        # Remove lines with mostly numbers (likely tables/figures)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if len(line.strip()) > 10:  # Keep lines with substantial content
                digit_ratio = sum(c.isdigit() for c in line) / len(line)
                if digit_ratio < 0.5:  # Keep lines that aren't mostly numbers
                    cleaned_lines.append(line.strip())
        
        return '\n'.join(cleaned_lines)
    
    def extract_sections(self, text):
        """Extract key sections from the text"""
        sections = {
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'full_text': text
        }
        
        # Common section headers
        section_patterns = {
            'abstract': r'(?i)(abstract|summary)',
            'introduction': r'(?i)(introduction|background)',
            'methods': r'(?i)(methods?|methodology|materials? and methods?)',
            'results': r'(?i)(results?|findings)',
            'discussion': r'(?i)(discussion|analysis)',
            'conclusion': r'(?i)(conclusion|conclusions?|summary)'
        }
        
        text_lower = text.lower()
        
        for section_name, pattern in section_patterns.items():
            matches = list(re.finditer(pattern, text_lower))
            if matches:
                start_pos = matches[0].start()
                # Find the next section or end of text
                next_pos = len(text)
                for other_pattern in section_patterns.values():
                    if other_pattern != pattern:
                        other_matches = list(re.finditer(other_pattern, text_lower[start_pos + 50:]))
                        if other_matches:
                            candidate_pos = start_pos + 50 + other_matches[0].start()
                            if candidate_pos < next_pos:
                                next_pos = candidate_pos
                
                sections[section_name] = text[start_pos:next_pos].strip()
        
        return sections
    
    def process_all_pdfs(self):
        """Process all PDFs in the directory"""
        pdf_files = list(Path(self.pdf_dir).glob("*.pdf"))
        processed_count = 0
        
        for pdf_file in pdf_files:
            print(f"Processing {pdf_file.name}...")
            
            # Check if already processed
            output_file = os.path.join(self.output_dir, f"{pdf_file.stem}.json")
            if os.path.exists(output_file):
                print(f"Skipping {pdf_file.name} - already processed")
                continue
            
            # Extract text
            raw_text = self.extract_text_from_pdf(pdf_file)
            if not raw_text:
                continue
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            if len(cleaned_text) < 100:  # Skip very short texts
                print(f"Skipping {pdf_file.name} - text too short")
                continue
            
            # Extract sections
            sections = self.extract_sections(cleaned_text)
            
            # Save processed data
            output_data = {
                'filename': pdf_file.name,
                'word_count': len(cleaned_text.split()),
                'sections': sections
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processed_count += 1
            print(f"Processed {pdf_file.name} ({len(cleaned_text.split())} words)")
        
        print(f"\nCompleted! Processed {processed_count} PDFs")
        return processed_count

if __name__ == "__main__":
    pdf_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    output_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\extracted_texts"
    
    extractor = TextExtractor(pdf_dir, output_dir)
    extractor.process_all_pdfs()