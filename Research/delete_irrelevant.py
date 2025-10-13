import json
import os

def delete_zero_relevance_articles():
    """Delete PDF files with relevance score of 0 based on research_metadata.json"""
    
    # Paths
    output_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research"
    articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    metadata_file = os.path.join(output_dir, "research_metadata.json")
    
    # Check if metadata file exists
    if not os.path.exists(metadata_file):
        print(f"Error: {metadata_file} not found")
        print("Please run batch_process.py first to generate the metadata file")
        return
    
    # Load metadata
    with open(metadata_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Find articles with relevance score of 0
    zero_relevance = [r for r in results if r.get('relevance_score', 0) == 0]
    
    if not zero_relevance:
        print("No articles found with relevance score of 0")
        return
    
    # Display articles to be deleted
    print(f"{'='*80}")
    print(f"Found {len(zero_relevance)} articles with relevance score of 0:")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(zero_relevance, 1):
        title = item.get('title', 'No title')
        filename = item['filename']
        print(f"{i}. {filename}")
        print(f"   Title: {title[:70]}{'...' if len(title) > 70 else ''}")
        print()
    
    # Confirm deletion
    print(f"{'='*80}")
    response = input(f"Delete these {len(zero_relevance)} PDF files? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Deletion cancelled")
        return
    
    # Delete files
    print(f"\n{'='*80}")
    print("Deleting files...")
    print(f"{'='*80}\n")
    
    deleted_count = 0
    error_count = 0
    
    for item in zero_relevance:
        filename = item['filename']
        pdf_path = os.path.join(articles_dir, filename)
        
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                deleted_count += 1
                print(f"✓ Deleted: {filename}")
            else:
                print(f"✗ Not found: {filename}")
                error_count += 1
        except Exception as e:
            print(f"✗ Error deleting {filename}: {e}")
            error_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"Summary:")
    print(f"  Successfully deleted: {deleted_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*80}")

if __name__ == "__main__":
    delete_zero_relevance_articles()
