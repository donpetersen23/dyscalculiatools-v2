import pandas as pd
import re

def clean_text(text):
    """Clean and format text for better readability"""
    if pd.isna(text) or text == '':
        return text
    
    # Remove extra quotes and escape characters
    text = str(text).strip('"').replace('\\"', '"').replace('\\n', ' ')
    
    # Break long sentences at natural points
    text = re.sub(r'(\. )([A-Z])', r'\1\n• \2', text)
    
    # Limit line length for readability
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) > 80:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
        else:
            current_line.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

def format_spreadsheets():
    """Format both research metadata and relevance scores for better readability"""
    
    # Format research metadata
    try:
        df1 = pd.read_csv(r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles\research_metadata.csv")
        
        if 'Summary' in df1.columns:
            df1['Summary'] = df1['Summary'].apply(clean_text)
        
        df1.to_csv(r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles\research_metadata_formatted.csv", 
                   index=False, encoding='utf-8')
        print("✓ Formatted research_metadata.csv")
        
    except Exception as e:
        print(f"Error formatting research metadata: {e}")
    
    # Format relevance scores
    try:
        df2 = pd.read_csv(r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\dyscalculia_relevance_scores.csv")
        
        if 'Abstract_Preview' in df2.columns:
            df2['Abstract_Preview'] = df2['Abstract_Preview'].apply(clean_text)
        
        df2.to_csv(r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\dyscalculia_relevance_scores_formatted.csv", 
                   index=False, encoding='utf-8')
        print("✓ Formatted dyscalculia_relevance_scores.csv")
        
    except Exception as e:
        print(f"Error formatting relevance scores: {e}")

if __name__ == "__main__":
    format_summaries()
    print("\nFormatted files created with '_formatted' suffix")
    print("Original files preserved unchanged")