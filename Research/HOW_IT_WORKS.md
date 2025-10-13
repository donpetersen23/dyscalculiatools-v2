# How the PDF Research Analyzer Works

## Overview
This tool automatically extracts metadata and generates analysis from PDF research articles using AWS Bedrock AI models.

## Process Flow

### 1. PDF Text Extraction
- Reads first 15 pages of each PDF
- Extracts key sections: Abstract, Introduction, Discussion/Conclusion
- Falls back to first 8000 characters if sections not found

### 2. Two-Stage AI Analysis
**Stage 1 - Metadata Extraction (Nova Micro)**
- Extracts: title, authors, publication year, DOI
- Fast and cost-effective for basic information

**Stage 2 - Content Analysis (Nova Premier)**
- Generates: summary, research category, tags, applicability scores
- Uses Abstract and Discussion sections for focused analysis

### 3. Data Processing
- Creates academic naming convention (LastName2024)
- Handles duplicate names with letters (Smith2024a, Smith2024b)
- Tracks token usage and costs

### 4. Export Formats
- **JSON**: Complete structured data
- **CSV**: Spreadsheet-friendly format

## File Sharing

### Upload Results
```python
from file_uploader import FileUploader
uploader = FileUploader()
uploader.upload_results()
```

### Access Shared Files
Check the `shared_files/` directory for timestamped results.

## Cost Structure
- Nova Micro: $0.000035 per 1K input tokens, $0.00014 per 1K output tokens
- Nova Premier: $0.0025 per 1K input tokens, $0.0125 per 1K output tokens
- Typical cost: ~$0.01-0.02 per PDF

## Requirements
- AWS account with Bedrock access
- Nova Micro and Nova Premier model access enabled
- Python packages: boto3, pandas, PyPDF2