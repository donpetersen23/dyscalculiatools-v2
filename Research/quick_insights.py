import os
from pdf_analyzer import PDFAnalyzer

def analyze_research_categories():
    """Analyze PDFs in organized research categories"""
    base_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\research articles"
    
    categories = {
        "Causes": os.path.join(base_dir, "Causes"),
        "Individualized Interventions": os.path.join(base_dir, "Individualized Interventions"),
        "Neuropsychological Interventions": os.path.join(base_dir, "Neuropsychological Interventions"),
        "Tier 2 Intervention": os.path.join(base_dir, "Tier 2 Intervention")
    }
    
    all_insights = {}
    
    for category, folder_path in categories.items():
        if os.path.exists(folder_path):
            print(f"\n{'='*60}")
            print(f"ANALYZING CATEGORY: {category.upper()}")
            print(f"{'='*60}")
            
            analyzer = PDFAnalyzer(folder_path)
            results = analyzer.analyze_all_pdfs()
            
            if results:
                report = analyzer.generate_summary_report()
                all_insights[category] = {
                    'results': results,
                    'report': report
                }
                print(report)
            else:
                print(f"No PDFs found in {category}")
    
    return all_insights

def quick_analysis_main_articles():
    """Quick analysis of main articles folder"""
    articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    print("QUICK ANALYSIS OF MAIN ARTICLES COLLECTION")
    print("="*60)
    
    analyzer = PDFAnalyzer(articles_dir)
    
    # Analyze first 10 files for quick insights
    results = analyzer.analyze_all_pdfs(max_files=10)
    
    if results:
        # Generate and display summary
        report = analyzer.generate_summary_report()
        print(report)
        
        # Save results
        analyzer.save_results("quick_analysis_results.json")
        analyzer.create_csv_summary("quick_analysis_summary.csv")
        
        return results
    else:
        print("No PDFs could be analyzed")
        return []

if __name__ == "__main__":
    print("DYSCALCULIA RESEARCH INSIGHTS ANALYZER")
    print("="*60)
    
    # First analyze organized categories
    category_insights = analyze_research_categories()
    
    print("\n\n" + "="*80)
    print("QUICK ANALYSIS OF MAIN COLLECTION")
    print("="*80)
    
    # Then do quick analysis of main collection
    main_results = quick_analysis_main_articles()
    
    print(f"\nAnalysis complete! Found insights from {len(main_results)} papers in main collection.")
    print("Check the generated JSON and CSV files for detailed results.")