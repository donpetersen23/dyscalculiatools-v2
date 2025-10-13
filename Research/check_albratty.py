import PyPDF2
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('articles/Albratty2025.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    full_text = ""
    for i in range(len(reader.pages)):
        full_text += reader.pages[i].extract_text()
    
    # Find dyscalculia mentions
    text_lower = full_text.lower()
    idx = text_lower.find('dyscalculia')
    
    if idx != -1:
        print("DYSCALCULIA FOUND IN ALBRATTY2025")
        print("="*60)
        print(f"\nContext around 'dyscalculia':")
        print(full_text[max(0, idx-300):idx+500])
        
        # Check if it's about intervention
        if 'intervention' in full_text[max(0, idx-500):idx+500].lower():
            print("\n\n*** INTERVENTION MENTIONED NEAR DYSCALCULIA ***")
    else:
        print("Dyscalculia not found")
