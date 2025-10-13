import os
import json
import boto3
import PyPDF2
from datetime import datetime
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tag_manager import TagManager
from prompt_templates import ANALYSIS_PROMPT

class BedrockPDFAnalyzer:
    def __init__(self, pdf_directory, output_directory=None, region='us-east-1', max_workers=2):
        self.pdf_directory = pdf_directory
        self.output_directory = output_directory or pdf_directory
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.results = []
        self.max_workers = max_workers
        self.lock = Lock()
        # Nova Micro pricing (input, output per 1K tokens)
        self.input_price = 0.000035
        self.output_price = 0.00014
        self.tag_manager = TagManager(self.output_directory, self.bedrock)
        
    def extract_text_from_pdf(self, pdf_path, max_pages=15):
        """Extract text from PDF focusing on abstract, introduction, and discussion/conclusion"""
        try:
            # Prevent path traversal attacks
            resolved_path = os.path.realpath(pdf_path)
            allowed_dir = os.path.realpath(self.pdf_directory)
            if not resolved_path.startswith(allowed_dir + os.sep):
                raise ValueError(f"Access denied: path outside allowed directory")
            
            with open(resolved_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                footer_text = ""
                
                for i, page in enumerate(reader.pages[:max_pages]):
                    page_text = page.extract_text()
                    full_text += page_text + "\n"
                    
                    # Extract potential footer info from first few pages
                    if i < 3:  # First 3 pages likely to have publication info
                        lines = page_text.split('\n')
                        # Get last few lines of each page (potential footer)
                        if len(lines) > 3:
                            footer_text += " ".join(lines[-3:]) + " "
                
                # Extract key sections
                sections, sections_found = self._extract_key_sections(full_text, footer_text)
                return sections, sections_found
        except Exception as e:
            import logging
            logging.error(f"Error reading {pdf_path}: {e}", exc_info=True)
            return ""
    
    def _extract_key_sections(self, full_text, footer_text=""):
        """Extract abstract, introduction, and discussion/conclusion sections"""
        text_lower = full_text.lower()
        sections = []
        sections_found = []
        
        # Always include first 1000 characters for title/author/year info
        header_section = full_text[:1000]
        sections.append(f"HEADER/TITLE SECTION:\n{header_section}")
        sections_found.append("Header/Title")
        
        # Include footer info from page bottoms (DOI, publication details)
        if footer_text.strip():
            sections.append(f"FOOTER SECTION:\n{footer_text[:500]}")
            sections_found.append("Footer")
        
        # Common section headers to look for
        abstract_markers = ['abstract', 'summary']
        intro_markers = ['introduction', '1. introduction', '1 introduction']
        discussion_markers = ['discussion', 'conclusion', 'conclusions', 'implications', 'limitations']
        
        # Find abstract
        abstract = self._find_section(full_text, text_lower, abstract_markers, max_length=1500)
        if abstract:
            sections.append(f"ABSTRACT:\n{abstract}")
            sections_found.append("Abstract")
        
        # Find introduction
        intro = self._find_section(full_text, text_lower, intro_markers, max_length=2000)
        if intro:
            sections.append(f"INTRODUCTION:\n{intro}")
            sections_found.append("Introduction")
        
        # Find discussion/conclusion
        discussion = self._find_section(full_text, text_lower, discussion_markers, max_length=2000)
        if discussion:
            sections.append(f"DISCUSSION/CONCLUSION:\n{discussion}")
            sections_found.append("Discussion/Conclusion")
        
        # If no sections found, fall back to first 8000 characters
        if len(sections) == 1:  # Only header section found
            return full_text[:8000], ["First 8000 characters (no sections detected)"]
        
        return "\n\n".join(sections)[:8000], sections_found
    
    def _find_section(self, full_text, text_lower, markers, max_length=3000):
        """Find a section based on common headers"""
        for marker in markers:
            start_pos = text_lower.find(marker)
            if start_pos != -1:
                # Look for the next section or end of reasonable length
                section_text = full_text[start_pos:start_pos + max_length]
                
                # Try to find a natural ending (next major section)
                next_section_markers = ['method', 'results', 'discussion', 'conclusion', 'references', 'acknowledgment']
                for next_marker in next_section_markers:
                    next_pos = section_text.lower().find(next_marker, len(marker) + 50)  # Skip the current marker
                    if next_pos != -1:
                        section_text = section_text[:next_pos]
                        break
                
                return section_text.strip()
        return None
    

    def _decode_html_entities(self, data):
        """Decode HTML entities in strings and lists"""
        if isinstance(data, str):
            return html.unescape(data)
        elif isinstance(data, list):
            return [html.unescape(v) if isinstance(v, str) else v for v in data]
        return data
    
    def extract_metadata_with_micro(self, text_data, filename):
        """Use Nova Micro to extract basic metadata only"""
        # Handle both old format (just text) and new format (text, sections_found)
        if isinstance(text_data, tuple):
            text, sections_found = text_data
        else:
            text, sections_found = text_data, ["Unknown sections"]
        
        # Create metadata-focused prompt
        metadata_prompt = f"""Extract ONLY the following basic metadata from this research article in JSON format:

1. title: Article title (string)
2. authors: List of author names (array of strings)
3. publication_year: Year of publication (integer)
4. doi: DOI number, journal URL, or publication link if available (or 'Not found' if none)

Article text:
{text[:2000]}

Respond ONLY with valid JSON:
{{
  "title": "Article Title",
  "authors": ["Author Name"],
  "publication_year": 2024,
  "doi": "DOI or 'Not found'"
}}"""

        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": metadata_prompt}]}],
                "inferenceConfig": {"max_new_tokens": 500}
            }
            
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-micro-v1:0',
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Get token usage
            input_tokens = result['usage']['inputTokens']
            output_tokens = result['usage']['outputTokens']
            cost = (input_tokens / 1000 * self.input_price) + (output_tokens / 1000 * self.output_price)
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                metadata = json.loads(content[json_start:json_end])
                
                # Decode HTML entities
                for key, value in metadata.items():
                    metadata[key] = self._decode_html_entities(value)
                
                metadata['_input_tokens'] = input_tokens
                metadata['_output_tokens'] = output_tokens
                metadata['_estimated_cost'] = f"{cost:.6f}"
                metadata['_sections_analyzed'] = sections_found
                metadata['_model_used'] = 'nova-micro'
                return metadata
                
        except Exception as e:
            print(f"Bedrock error for {filename}: {e}")
        
        return None
    
    def analyze_content_with_premier(self, text_data, filename, metadata):
        """Use Nova Premier to analyze research content"""
        if isinstance(text_data, tuple):
            text, sections_found = text_data
        else:
            text, sections_found = text_data, ["Unknown sections"]
        
        # Extract only Abstract and Discussion/Conclusion sections
        content_sections = []
        if "Abstract" in sections_found:
            abstract_start = text.find("ABSTRACT:")
            if abstract_start != -1:
                content_sections.append(text[abstract_start:abstract_start+1500])
        
        if "Discussion/Conclusion" in sections_found:
            disc_start = text.find("DISCUSSION/CONCLUSION:")
            if disc_start != -1:
                content_sections.append(text[disc_start:disc_start+2000])
        
        # Use Abstract + Discussion or fallback to full text
        content_text = "\n\n".join(content_sections) if content_sections else text[:4000]
        
        # Create content-only prompt (no metadata)
        content_prompt = f"""{ANALYSIS_PROMPT}

Article text:
{content_text}"""
        
        try:
            body = {
                "messages": [{"role": "user", "content": [{"text": content_prompt}]}],
                "inferenceConfig": {"max_new_tokens": 2000}
            }
            
            response = self.bedrock.invoke_model(
                modelId='us.amazon.nova-premier-v1:0',
                body=json.dumps(body)
            )
            
            result = json.loads(response['body'].read())
            content = result['output']['message']['content'][0]['text']
            
            # Get token usage
            input_tokens = result['usage']['inputTokens']
            output_tokens = result['usage']['outputTokens']
            premier_cost = (input_tokens / 1000 * 0.0025) + (output_tokens / 1000 * 0.0125)
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                analysis = json.loads(content[json_start:json_end])
                
                # Merge content analysis (skip metadata fields)
                for key, value in analysis.items():
                    if key not in ['authors', 'publication_year', 'title', 'doi']:  # Skip metadata
                        if key == 'tags':
                            decoded_tags = self._decode_html_entities(value)
                            metadata[key] = self.tag_manager.process_tags(decoded_tags, filename, metadata)
                        else:
                            metadata[key] = self._decode_html_entities(value)
                
                # Update cost tracking
                metadata['_premier_input_tokens'] = input_tokens
                metadata['_premier_output_tokens'] = output_tokens
                metadata['_premier_cost'] = f"{premier_cost:.6f}"
                metadata['_total_cost'] = metadata.get('_estimated_cost', 0) + premier_cost
                metadata['_model_used'] = 'nova-micro + nova-premier'
                
                return metadata
                
        except Exception as e:
            print(f"Premier analysis error for {filename}: {e}")
        
        return metadata
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file with both Micro and Premier in parallel"""
        filename = os.path.basename(pdf_path)
        print(f"Processing: {filename}")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        # Run both models in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            micro_future = executor.submit(self.extract_metadata_with_micro, text, filename)
            premier_future = executor.submit(self.analyze_content_with_premier, text, filename, {})
            
            # Get results
            metadata = micro_future.result()
            if not metadata:
                return None
                
            analysis = premier_future.result()
            
            # Merge results
            if analysis:
                for key, value in analysis.items():
                    if not key.startswith('_'):  # Don't overwrite metadata fields
                        metadata[key] = value
                
                # Combine cost tracking
                metadata['_premier_input_tokens'] = analysis.get('_premier_input_tokens', 0)
                metadata['_premier_output_tokens'] = analysis.get('_premier_output_tokens', 0)
                metadata['_premier_cost'] = analysis.get('_premier_cost', 0)
                
                # Calculate totals
                micro_cost = float(metadata.get('_estimated_cost', 0))
                premier_cost = float(analysis.get('_premier_cost', 0))
                metadata['_total_cost'] = f"{micro_cost + premier_cost:.6f}"
                
                # Total tokens
                metadata['_total_input_tokens'] = metadata.get('_input_tokens', 0) + analysis.get('_premier_input_tokens', 0)
                metadata['_total_output_tokens'] = metadata.get('_output_tokens', 0) + analysis.get('_premier_output_tokens', 0)
                
                metadata['_model_used'] = 'nova-micro + nova-premier (parallel)'
        
        metadata['filename'] = filename
        metadata['file_path'] = pdf_path
        metadata['processed_date'] = datetime.now().isoformat()
        return metadata
    
    def process_all_pdfs(self, max_files=None):
        """Process all PDFs in directory with parallel processing"""
        pdf_files = [f for f in os.listdir(self.pdf_directory) if f.lower().endswith('.pdf')]
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        total_files = len(pdf_files)
        print(f"Found {total_files} PDF files")
        print(f"Processing with {self.max_workers} parallel workers...\n")
        
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.process_pdf, os.path.join(self.pdf_directory, pdf_file)): pdf_file 
                for pdf_file in pdf_files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                pdf_file = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.results.append(result)
                            completed += 1
                            percentage = (completed / total_files) * 100
                            print(f"Progress: {completed}/{total_files} ({percentage:.1f}%)")
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}")
        
        print(f"\nCompleted processing {completed} files")
        return self.results
    
    def save_results(self, filename):
        """Save results to JSON file"""
        output_path = os.path.join(self.output_directory, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_path}")
    
    def generate_report(self):
        """Generate a summary report of the processing results"""
        if not self.results:
            return "No results to report."
        
        total_files = len(self.results)
        total_cost = sum(float(result.get('_total_cost', 0)) for result in self.results)
        
        # Separate token tracking
        micro_input_tokens = sum(result.get('_input_tokens', 0) for result in self.results)
        micro_output_tokens = sum(result.get('_output_tokens', 0) for result in self.results)
        premier_input_tokens = sum(result.get('_premier_input_tokens', 0) for result in self.results)
        premier_output_tokens = sum(result.get('_premier_output_tokens', 0) for result in self.results)
        total_input_tokens = micro_input_tokens + premier_input_tokens
        total_output_tokens = micro_output_tokens + premier_output_tokens
        
        # Separate cost tracking
        micro_cost = sum(float(result.get('_estimated_cost', 0)) for result in self.results)
        premier_cost = sum(float(result.get('_premier_cost', 0)) for result in self.results)
        
        # Count research categories
        categories = {}
        for result in self.results:
            category = result.get('research_category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        report = f"""PROCESSING SUMMARY:
- Files processed: {total_files}
- Total estimated cost: ${total_cost:.6f}

COST BREAKDOWN:
- Nova Micro (metadata): ${micro_cost:.6f}
- Nova Premier (analysis): ${premier_cost:.6f}

TOKEN USAGE:
- Total input tokens: {total_input_tokens:,} (Micro: {micro_input_tokens:,}, Premier: {premier_input_tokens:,})
- Total output tokens: {total_output_tokens:,} (Micro: {micro_output_tokens:,}, Premier: {premier_output_tokens:,})

RESEARCH CATEGORIES:"""
        
        for category, count in sorted(categories.items()):
            report += f"\n- {category}: {count}"
        
        return report
