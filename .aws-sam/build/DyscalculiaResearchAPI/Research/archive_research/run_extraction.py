from text_extractor import TextExtractor

if __name__ == "__main__":
    pdf_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    output_dir = r"C:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\extracted_texts"
    
    print("Starting text extraction from PDFs...")
    extractor = TextExtractor(pdf_dir, output_dir)
    count = extractor.process_all_pdfs()
    print(f"Text extraction complete! Processed {count} files.")