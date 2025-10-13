import pandas as pd
import os
import shutil

def rename_files():
    """Rename files from Filename_1 to Filename_2 using CSV mapping"""
    
    # Paths
    csv_path = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\research_metadata.csv"
    articles_dir = r"c:\Users\donpe\OneDrive\OneDrive_3_7-12-2022\dyscalculiatools\Research\articles"
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    renamed_count = 0
    errors = []
    
    print("Starting file renaming process...")
    
    for _, row in df.iterrows():
        filename_1 = row['Filename_1']
        filename_2 = row['Filename_2']
        
        # Construct full paths
        old_path = os.path.join(articles_dir, filename_1)
        new_path = os.path.join(articles_dir, f"{filename_2}.pdf")
        
        # Check if source file exists
        if os.path.exists(old_path):
            try:
                # Check if target already exists
                if os.path.exists(new_path):
                    print(f"Target already exists: {filename_2}.pdf")
                    continue
                
                # Rename the file
                shutil.move(old_path, new_path)
                print(f"Renamed: {filename_1} -> {filename_2}.pdf")
                renamed_count += 1
                
            except Exception as e:
                error_msg = f"Error renaming {filename_1}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        else:
            error_msg = f"File not found: {filename_1}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\nRenaming complete!")
    print(f"Successfully renamed: {renamed_count} files")
    
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for error in errors:
            print(f"  - {error}")

if __name__ == "__main__":
    rename_files()