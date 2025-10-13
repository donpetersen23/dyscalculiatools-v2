import json
import os
from batch_process import process_and_export
from bedrock_pdf_analyzer import BedrockPDFAnalyzer

def continue_processing():
    """Continue processing from where we left off"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load existing results
    existing_file = os.path.join(script_dir, "research_metadata.json")
    processed_files = set()
    
    if os.path.exists(existing_file):
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
            processed_files = {result['filename'] for result in existing_results}
        print(f"Found {len(processed_files)} already processed files")
    
    # Get all PDF files
    articles_dir = os.path.join(script_dir, "articles")
    all_pdfs = [f for f in os.listdir(articles_dir) if f.lower().endswith('.pdf')]
    remaining_pdfs = [f for f in all_pdfs if f not in processed_files]
    
    print(f"Total PDFs: {len(all_pdfs)}")
    print(f"Remaining to process: {len(remaining_pdfs)}")
    
    if not remaining_pdfs:
        print("All files already processed!")
        return
    
    # Process remaining files
    analyzer = BedrockPDFAnalyzer(articles_dir, script_dir)
    analyzer.results = existing_results if os.path.exists(existing_file) else []
    
    print(f"Continuing with {len(remaining_pdfs)} files...")
    
    # Process each remaining file
    for i, pdf_file in enumerate(remaining_pdfs, 1):
        try:
            print(f"Processing {i}/{len(remaining_pdfs)}: {pdf_file}")
            pdf_path = os.path.join(articles_dir, pdf_file)
            result = analyzer.process_pdf(pdf_path)
            if result:
                analyzer.results.append(result)
                # Save after each file to avoid losing progress
                analyzer.save_results("research_metadata.json")
        except KeyboardInterrupt:
            print(f"\nInterrupted. Processed {i-1} additional files.")
            break
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    # Final export
    process_and_export()

if __name__ == "__main__":
    continue_processing()