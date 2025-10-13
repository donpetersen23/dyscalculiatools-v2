import pandas as pd
from bedrock_pdf_analyzer import BedrockPDFAnalyzer
import os

def process_and_export(articles_dir=None, output_dir=None, max_files=None):
    """Process PDFs and export to multiple formats"""
    # Set default paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    articles_dir = articles_dir or os.path.join(script_dir, "articles")
    output_dir = output_dir or script_dir
    
    # Validate directories exist
    if not os.path.isdir(articles_dir):
        print(f"ERROR: Articles directory does not exist: {articles_dir}")
        return
    if not os.path.isdir(output_dir):
        print(f"ERROR: Output directory does not exist: {output_dir}")
        return
    
    # Initialize analyzer and process PDFs
    analyzer = BedrockPDFAnalyzer(articles_dir, output_dir)
    print("Processing PDFs with AWS Bedrock...")
    results = analyzer.process_all_pdfs(max_files=max_files)
    
    if not results:
        print("No results to export")
        return
    
    # Save JSON
    analyzer.save_results("research_metadata.json")
    
    # Prepare DataFrame
    df = pd.DataFrame(results)
    df['authors_str'] = df['authors'].apply(lambda x: '; '.join(x) if isinstance(x, list) else str(x))
    df['tags_str'] = df['tags'].apply(lambda x: '; '.join(x) if isinstance(x, list) else str(x))
    
    # Add missing columns
    for col in ['relevance_score', 'one_on_one_applicability', 'small_group_applicability', 
                'large_group_applicability', 'self_education_applicability']:
        if col not in df.columns:
            df[col] = ''
    
    # Create academic naming convention
    def create_academic_name(row):
        year = str(row.get('publication_year', 'Unknown'))
        authors = row.get('authors', [])
        if authors and len(authors) > 0:
            last_name = str(authors[0]).split()[-1] if authors[0] else "Unknown"
            return f"{last_name}{year}"
        return f"Unknown{year}"
    
    df['academic_name_base'] = df.apply(create_academic_name, axis=1)
    
    # Handle duplicate names
    name_counts = {}
    academic_names = []
    for name in df['academic_name_base']:
        if name in name_counts:
            name_counts[name] += 1
            letter = chr(ord('a') + name_counts[name] - 1)
            academic_names.append(f"{name}{letter}")
        else:
            name_counts[name] = 1
            academic_names.append(name)
    df['filename_2'] = academic_names
    
    # Prepare sections_analyzed string
    df['sections_analyzed_str'] = df.get('_sections_analyzed', pd.Series()).apply(
        lambda x: '; '.join(x) if isinstance(x, list) else str(x) if pd.notna(x) else ''
    )
    
    # Export to CSV
    csv_df = df[[
        'filename', 'filename_2', 'title', 'authors_str', 'publication_year',
        'relevance_score', 'research_category', 'summary', 'tags_str', 'doi',
        'one_on_one_applicability', 'small_group_applicability', 
        'large_group_applicability', 'self_education_applicability',
        'sections_analyzed_str', '_input_tokens', '_output_tokens', '_total_cost'
    ]]
    
    csv_df.columns = [
        'Filename_1', 'Filename_2', 'Title', 'Authors', 'Year', 'Relevance Score',
        'Research Category', 'Summary', 'Tags', 'DOI/URL',
        'One-on-One Applicability', 'Small Group Applicability', 
        'Large Group Applicability', 'Self Education Applicability',
        'Sections Analyzed', 'Input Tokens', 'Output Tokens', 'Estimated Cost'
    ]
    
    try:
        csv_df.to_csv(os.path.join(output_dir, "research_metadata.csv"), index=False, encoding='utf-8')
        print(f"\nProcessed {len(results)} articles")
        print("Results saved to research_metadata.json and research_metadata.csv")
    except PermissionError:
        print(f"\nProcessed {len(results)} articles")
        print("Results saved to research_metadata.json")
        print("Warning: Could not save CSV (file may be open in another program)")
    
    print("\n" + analyzer.generate_report())

if __name__ == "__main__":
    process_and_export()
