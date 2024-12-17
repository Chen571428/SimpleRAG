import os
import shutil
import argparse
import math

class MarkdownCopier:
    def __init__(self, source_dir, target_dir, group_size=None, flat_structure=False):
        self.source_dir = os.path.abspath(source_dir)
        self.target_dir = os.path.abspath(target_dir)
        self.group_size = group_size
        self.flat_structure = flat_structure
        self.file_count = 0
        self.md_files = []

    def collect_markdown_files(self):
        """Collect all markdown files from source directory"""
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith(('.md', '.markdown','.pdf')):
                    source_file = os.path.join(root, file)
                    relative_path = os.path.relpath(root, self.source_dir)
                    self.md_files.append((source_file, relative_path, file))
        return len(self.md_files)

    def copy_with_groups(self):
        """Copy files with grouping"""
        total_files = len(self.md_files)
        if total_files == 0:
            print("No markdown files found in source directory")
            return

        if self.group_size:
            num_groups = math.ceil(total_files / self.group_size)
            print(f"Organizing {total_files} files into {num_groups} groups of {self.group_size} files each")
            
            for i, (source_file, relative_path, file) in enumerate(self.md_files):
                group_num = i // self.group_size + 1
                group_dir = os.path.join(self.target_dir, f"group_{group_num:03d}")
                
                if relative_path != '.':
                    target_path = os.path.join(group_dir, relative_path)
                else:
                    target_path = group_dir
                
                os.makedirs(target_path, exist_ok=True)
                target_file = os.path.join(target_path, file)
                self._copy_file(source_file, target_file)
        else:
            self.copy_without_groups()

    def copy_without_groups(self):
        """Copy files with or without original directory structure"""
        for source_file, relative_path, file in self.md_files:
            if self.flat_structure:
                # If flat structure is requested, ignore relative_path
                target_path = self.target_dir
            else:
                # Keep original structure
                if relative_path != '.':
                    target_path = os.path.join(self.target_dir, relative_path)
                else:
                    target_path = self.target_dir
            
            os.makedirs(target_path, exist_ok=True)
            target_file = os.path.join(target_path, file)
            
            # Handle filename conflicts in flat structure
            if self.flat_structure and os.path.exists(target_file):
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(target_file):
                    new_name = f"{base}_{counter}{ext}"
                    target_file = os.path.join(target_path, new_name)
                    counter += 1
                
            self._copy_file(source_file, target_file)

    def _copy_file(self, source_file, target_file):
        """Copy a single file and print progress"""
        shutil.copy2(source_file, target_file)
        self.file_count += 1
        print(f"Copied ({self.file_count}): {source_file} -> {target_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Copy markdown files from source directory to target directory with optional grouping'
    )
    parser.add_argument(
        'source_dir',
        help='Source directory containing markdown files'
    )
    parser.add_argument(
        'target_dir',
        help='Target directory where markdown files will be copied to'
    )
    parser.add_argument(
        '-g', '--group-size',
        type=int,
        help='Number of files per group (optional)',
        default=None
    )
    parser.add_argument(
        '-f', '--flat',
        action='store_true',
        help='Copy files to target directory without preserving directory structure'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory '{args.source_dir}' does not exist")
        return
    
    try:
        copier = MarkdownCopier(args.source_dir, args.target_dir, args.group_size, args.flat)
        total_files = copier.collect_markdown_files()
        
        if total_files > 0:
            if args.group_size:
                print(f"Found {total_files} markdown files. Will organize into groups of {args.group_size}")
            else:
                print(f"Found {total_files} markdown files")
                
            copier.copy_with_groups()
            print("Markdown files copy completed successfully!")
        else:
            print("No markdown files found in source directory")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
