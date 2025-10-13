# AWS Bedrock PDF Research Article Analyzer

Automatically extract authors, publication years, and generate summaries from PDF research articles using AWS Bedrock AI.

## Features

- **Author Extraction**: Identifies all authors from research papers
- **Publication Year**: Extracts the publication year
- **AI-Generated Summaries**: Creates concise 3-4 sentence summaries using Claude
- **Batch Processing**: Process multiple PDFs at once
- **Multiple Export Formats**: JSON and CSV outputs

## Prerequisites

1. **AWS Account** with Bedrock access
2. **AWS Credentials** configured (via AWS CLI or environment variables)
3. **Bedrock Model Access**: Enable Claude 3 Haiku in your AWS account
   - Go to AWS Console → Bedrock → Model access
   - Request access to Anthropic Claude models

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials (if not already done):
```bash
aws configure
```

## Usage

### Process All PDFs

```python
python batch_process.py
```

### Process Specific Number of PDFs

```python
from bedrock_pdf_analyzer import BedrockPDFAnalyzer

articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
analyzer = BedrockPDFAnalyzer(articles_dir)

# Process first 10 PDFs
analyzer.process_all_pdfs(max_files=10)

# View results
print(analyzer.generate_report())

# Save results
analyzer.save_results()
```

## Output Files

- **research_metadata.json**: Complete results with all metadata
- **research_metadata.csv**: Spreadsheet-friendly format

## Cost Considerations

- Claude 3 Haiku: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens
- Processing ~150 PDFs ≈ $1-2 USD
- Most cost-effective Claude model for this task

## Customization

### Change AWS Region
```python
analyzer = BedrockPDFAnalyzer(articles_dir, region='us-west-2')
```

### Use Different Claude Model
Edit `bedrock_pdf_analyzer.py` line 48:
```python
modelId='anthropic.claude-3-sonnet-20240229-v1:0'  # More capable, higher cost
```

## Troubleshooting

**Error: "Could not connect to Bedrock"**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check Bedrock is available in your region

**Error: "Access denied to model"**
- Enable model access in AWS Console → Bedrock → Model access

**Poor extraction quality**
- Increase `max_pages` in `extract_text_from_pdf()` (default: 10)
- Use Claude Sonnet for better accuracy
