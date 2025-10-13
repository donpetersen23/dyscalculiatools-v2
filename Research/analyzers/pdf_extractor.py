import os
import PyPDF2
import logging

class PDFExtractor:
    """Handles PDF text extraction and section parsing"""
    
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
    
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
                for i, page in enumerate(reader.pages[:max_pages]):
                    full_text += page.extract_text() + "\n"
                
                # Extract key sections
                sections, sections_found = self._extract_key_sections(full_text)
                return sections, sections_found
        except Exception as e:
            logging.error(f"Error reading {pdf_path}: {e}", exc_info=True)
            return "", []
    
    def _extract_key_sections(self, full_text):
        """Extract abstract, introduction, and discussion/conclusion sections"""
        text_lower = full_text.lower()
        sections = []
        sections_found = []
        
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
        intro = self._find_section(full_text, text_lower, intro_markers, max_length=3000)
        if intro:
            sections.append(f"INTRODUCTION:\n{intro}")
            sections_found.append("Introduction")
        
        # Find discussion/conclusion
        discussion = self._find_section(full_text, text_lower, discussion_markers, max_length=3000)
        if discussion:
            sections.append(f"DISCUSSION/CONCLUSION:\n{discussion}")
            sections_found.append("Discussion/Conclusion")
        
        # If no sections found, fall back to first 8000 characters
        if not sections:
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