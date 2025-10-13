import os
import json
import boto3
from PyPDF2 import PdfReader
from collections import defaultdict
import fitz  # PyMuPDF
from io import BytesIO

class PDFRenamer:
    def __init__(self, aws_region='us-east-1'):
        self.textract = boto3.client('textract', region_name=aws_region)
        self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
        self.used_names = defaultdict(int)
        
    def extract_first_page_as_image(self, pdf_path):
        """Extract first page as PNG image for Textract"""
        doc = fitz.open(pdf_path)
        page = doc[0]  # First page
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_data = pix.tobytes("png")
        doc.close()
        return img_data
    
    def extract_text_textract(self, image_bytes):
        """Use AWS Textract to extract text from image"""
        response = self.textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )
        
        text = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                text.append(block['Text'])
        
        return '\n'.join(text)
    

    
    def parse_metadata_claude(self, text):
        """Use Claude to extract author and year from text"""
        prompt = f"""Extract the first author's last name and publication year from this academic paper text.

Text:
{text[:3000]}

Return ONLY a JSON object with this exact format:
{{"last_name": "AuthorLastName", "year": "YYYY"}}

If you cannot find the information, use null for that field."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        
        result = json.loads(response['body'].read())
        content = result['content'][0]['text']
        
        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            metadata = json.loads(content[start:end])
            return metadata.get('last_name'), metadata.get('year')
        
        return None, None
    
    def generate_filename(self, last_name, year):
        """Generate filename with duplicate handling"""
        if not last_name or not year:
            return None
        
        base_name = f"{last_name}{year}"
        key = base_name.lower()
        
        if self.used_names[key] == 0:
            self.used_names[key] = 1
            return f"{base_name}.pdf"
        else:
            self.used_names[key] += 1
            return f"{base_name}_{self.used_names[key]}.pdf"
    
    def rename_pdf(self, pdf_path, dry_run=False):
        """Rename a single PDF file"""
        try:
            print(f"Processing: {os.path.basename(pdf_path)}")
            
            # Extract first page as image
            image_bytes = self.extract_first_page_as_image(pdf_path)
            
            # Extract text with Textract
            text = self.extract_text_textract(image_bytes)
            
            # Parse with Claude
            last_name, year = self.parse_metadata_claude(text)
            
            if not last_name or not year:
                print(f"  ❌ Could not extract metadata")
                return False
            
            # Generate new filename
            new_filename = self.generate_filename(last_name, year)
            new_path = os.path.join(os.path.dirname(pdf_path), new_filename)
            
            if dry_run:
                print(f"  ✓ Would rename to: {new_filename}")
            else:
                os.rename(pdf_path, new_path)
                print(f"  ✓ Renamed to: {new_filename}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def rename_directory(self, directory, dry_run=False):
        """Rename all PDFs in a directory"""
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        
        print(f"Found {len(pdf_files)} PDF files")
        if dry_run:
            print("DRY RUN MODE - No files will be renamed\n")
        
        success = 0
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory, pdf_file)
            if self.rename_pdf(pdf_path, dry_run):
                success += 1
        
        print(f"\nCompleted: {success}/{len(pdf_files)} files processed successfully")

if __name__ == "__main__":
    # Configuration
    articles_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    renamer = PDFRenamer(aws_region='us-east-1')
    
    # Run in dry-run mode first to preview changes
    renamer.rename_directory(articles_dir, dry_run=True)
    
    # Uncomment to actually rename files:
    # renamer.rename_directory(articles_dir, dry_run=False)
