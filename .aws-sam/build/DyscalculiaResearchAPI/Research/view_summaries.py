import sqlite3
from pathlib import Path

def view_summaries(db_path):
    """View all paper summaries in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT filename, title, authors, year, paper_type, summary FROM papers ORDER BY year DESC, authors")
    papers = cursor.fetchall()
    
    if not papers:
        print("No papers found in database")
        return
    
    print(f"Found {len(papers)} papers in database\n")
    print("=" * 80)
    
    for i, (filename, title, authors, year, paper_type, summary) in enumerate(papers, 1):
        print(f"\n{i}. {filename}")
        print(f"   {title} ({year})")
        print(f"   Authors: {authors}")
        print(f"   Type: {paper_type}")
        print("-" * 80)
        print(summary)
        print("=" * 80)
    
    conn.close()

def search_summaries(db_path, search_term):
    """Search for papers containing specific terms"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT filename, title, authors, year, summary 
        FROM papers 
        WHERE title LIKE ? OR summary LIKE ? OR authors LIKE ?
        ORDER BY year DESC
    """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
    
    papers = cursor.fetchall()
    
    if not papers:
        print(f"No papers found containing '{search_term}'")
        return
    
    print(f"Found {len(papers)} papers containing '{search_term}'\n")
    
    for filename, title, authors, year, summary in papers:
        print(f"• {filename} - {title} ({year})")
        print(f"  Authors: {authors}")
        print()
    
    conn.close()

if __name__ == "__main__":
    db_path = Path(r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles\research_summaries.db")
    
    if not db_path.exists():
        print("Database not found. Run pdf_processor.py first.")
        exit()
    
    print("Research Paper Database Viewer")
    print("1. View all summaries")
    print("2. Search papers")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        view_summaries(db_path)
    elif choice == "2":
        search_term = input("Enter search term: ").strip()
        search_summaries(db_path, search_term)
    else:
        print("Invalid choice")