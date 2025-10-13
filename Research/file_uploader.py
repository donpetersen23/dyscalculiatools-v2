import os
import shutil
from datetime import datetime

class FileUploader:
    def __init__(self, upload_dir="shared_files"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def upload_results(self, source_json="research_metadata.json", source_csv="research_metadata.csv"):
        """Copy results to shared directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_copied = []
        for source_file in [source_json, source_csv]:
            if os.path.exists(source_file):
                name, ext = os.path.splitext(source_file)
                dest_file = os.path.join(self.upload_dir, f"{name}_{timestamp}{ext}")
                shutil.copy2(source_file, dest_file)
                files_copied.append(dest_file)
                print(f"Uploaded: {dest_file}")
        
        return files_copied
    
    def list_shared_files(self):
        """List all files in shared directory"""
        if not os.path.exists(self.upload_dir):
            return []
        return [f for f in os.listdir(self.upload_dir) if f.endswith(('.json', '.csv'))]

if __name__ == "__main__":
    uploader = FileUploader()
    uploader.upload_results()