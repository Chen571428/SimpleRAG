import argparse
from pathlib import Path
from step1_pdf_to_md import convert_pdf_to_md
from step2_split_md import split_markdown_files
from step3_process_images import process_images

def main():
    parser = argparse.ArgumentParser(
        description='Convert PDFs to Markdown and preprocess for RAG applications'
    )
    
    parser.add_argument(
        '-i', '--input_dir',
        required=True,
        help='Directory containing PDF files'
    )
    parser.add_argument(
        '-o', '--output_dir',
        required=True,
        help='Directory for output files'
    )
    parser.add_argument(
        '--picgo',
        default="http://127.0.0.1:36677",
        help='PicGO server endpoint (default: http://127.0.0.1:36677)'
    )
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    # 执行步骤3：处理图片
    if not process_images(args.output_dir, args.picgo):
        print("Step 3 failed. Stopping process.")
        return
    
    print("\nAll processing steps completed successfully!")
    print(f"Processed files can be found in: {args.output_dir}")

if __name__ == '__main__':
    main()