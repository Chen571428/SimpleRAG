import os
import argparse

class MarkdownRenamer:
    def __init__(self, source_dir):
        self.source_dir = os.path.abspath(source_dir)
        self.renamed_count = 0
        
    def rename_markdown_files(self):
        """Recursively rename all markdown files to txt"""
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    self._rename_file(root, file)
        
        return self.renamed_count
    
    def _rename_file(self, root, file):
        """Rename a single markdown file to txt"""
        file_path = os.path.join(root, file)
        base_name = os.path.splitext(file)[0]
        new_name = f"{base_name}.txt"
        new_path = os.path.join(root, new_name)
        
        # Handle case where .txt file already exists
        if os.path.exists(new_path):
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{base_name}_{counter}.txt"
                new_path = os.path.join(root, new_name)
                counter += 1
        
        try:
            os.rename(file_path, new_path)
            self.renamed_count += 1
            print(f"Renamed: {file} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {file}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='Rename all markdown files to txt in the specified directory'
    )
    parser.add_argument(
        'source_dir',
        help='Source directory containing markdown files'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Error: Directory '{args.source_dir}' does not exist")
        return
    
    try:
        renamer = MarkdownRenamer(args.source_dir)
        total_renamed = renamer.rename_markdown_files()
        
        if total_renamed > 0:
            print(f"\nSuccessfully renamed {total_renamed} files")
        else:
            print("No markdown files found in the specified directory")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

