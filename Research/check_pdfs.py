import PyPDF2
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

files = [
    'articles/Albratty2025.pdf',
    'articles/Ali2025.pdf', 
    'articles/Alkahtani2025.pdf'
]

for pdf_file in files:
    print(f"\n{'='*60}")
    print(f"FILE: {pdf_file}")
    print('='*60)
    try:
        with open(pdf_file, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(min(5, len(reader.pages))):
                text += reader.pages[i].extract_text()
            
            # Check for math intervention keywords
            keywords = ['mathematics', 'math', 'arithmetic', 'numerical', 
                       'calculation', 'dyscalculia', 'number sense', 'intervention']
            
            print(f"\nTitle: {text[:300].strip()}")
            print(f"\nKeyword matches:")
            found = []
            for kw in keywords:
                if kw.lower() in text.lower():
                    found.append(kw)
            print(f"  Found: {', '.join(found) if found else 'None'}")
            
            # Check if it's about math/dyscalculia
            is_math_related = any(kw in text.lower() for kw in ['dyscalculia', 'mathematics intervention', 'math intervention', 'arithmetic intervention'])
            print(f"\nMath intervention study: {'YES' if is_math_related else 'NO'}")
                
    except Exception as e:
        print(f"Error: {e}")
