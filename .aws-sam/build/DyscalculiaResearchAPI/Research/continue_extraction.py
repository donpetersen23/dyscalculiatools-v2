#!/usr/bin/env python3

import os
import json
from bedrock_pdf_analyzer import BedrockPDFAnalyzer

def continue_extraction():
    """Continue PDF extraction from where it left off"""
    
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_directory = os.path.join(current_dir, "articles")
    results_file = os.path.join(current_dir, "research_metadata.json")
    
    # Load existing results
    existing_results = []
    processed_files = set()
    
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
        processed_files = {result['filename'] for result in existing_results}
        print(f"Found {len(existing_results)} existing results")
    
    # Get all PDF files
    all_pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    remaining_files = [f for f in all_pdf_files if f not in processed_files]
    
    print(f"Total PDF files: {len(all_pdf_files)}")
    print(f"Already processed: {len(processed_files)}")
    print(f"Remaining to process: {len(remaining_files)}")
    
    if not remaining_files:
        print("All files have been processed!")
        return
    
    # Initialize analyzer
    analyzer = BedrockPDFAnalyzer(
        pdf_directory=pdf_directory,
        output_directory=current_dir,
        max_workers=2  # Conservative to avoid rate limits
    )
    
    # Load existing results into analyzer
    analyzer.results = existing_results.copy()
    
    # Process remaining files
    print(f"\nContinuing extraction with {len(remaining_files)} remaining files...")
    print("=" * 80)
    
    completed = len(existing_results)
    total_files = len(all_pdf_files)
    
    for pdf_file in remaining_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        
        try:
            print(f"Processing: {pdf_file}")
            result = analyzer.process_pdf(pdf_path)
            
            if result:
                analyzer.results.append(result)
                completed += 1
                percentage = (completed / total_files) * 100
                relevance = result.get('relevance_score', 'N/A')
                print(f"[{percentage:5.1f}%] {completed}/{total_files} - {pdf_file[:40]:40s} (Relevance: {relevance})")
                
                # Save results after each successful processing (backup)
                analyzer.save_results("research_metadata.json")
                
            else:
                print(f"Failed to process: {pdf_file}")
                
        except KeyboardInterrupt:
            print(f"\nInterrupted! Saving progress...")
            analyzer.save_results("research_metadata.json")
            analyzer.save_tags_metadata()
            print(f"Saved {len(analyzer.results)} results before interruption")
            return
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            continue
    
    # Final save and summary
    analyzer.save_results("research_metadata.json")
    analyzer.save_tags_metadata()
    
    # Print final summary
    total_cost = sum(r.get('_estimated_cost', 0) for r in analyzer.results)
    avg_cost = total_cost / len(analyzer.results) if analyzer.results else 0
    
    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE!")
    print(f"{'='*80}")
    print(f"Total files processed: {len(analyzer.results)}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Average per study: ${avg_cost:.6f}")
    
    # Print relevance distribution
    if analyzer.results:
        relevance_scores = [r.get('relevance_score', 0) for r in analyzer.results]
        print(f"\nRelevance Distribution:")
        print(f"  High (8-10): {sum(1 for s in relevance_scores if s >= 8)}")
        print(f"  Medium (5-7): {sum(1 for s in relevance_scores if 5 <= s < 8)}")
        print(f"  Low (0-4): {sum(1 for s in relevance_scores if s < 5)}")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    continue_extraction()