import os
import subprocess
import argparse
from pathlib import Path

def convert_pdfs_to_md(input_dir: str, output_dir: str) -> None:
    """
    将指定目录下的PDF文件转换为Markdown文件
    
    Args:
        input_dir (str): PDF文件所在的输入目录
        output_dir (str): Markdown文件的输出目录
    """
    # 确保输入输出路径都是绝对路径
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files to convert")
    
    # 遍历处理每个PDF文件
    for filename in pdf_files:
        input_path = os.path.join(input_dir, filename)
        print(f"\nProcessing: {filename}")
        
        try:
            # 构建marker_single���令
            command = [
                'marker_single',
                input_path,
                '--output_dir', output_dir,
                '--output_format', 'markdown',
                '--force_ocr'
            ]
            
            # 执行命令并等待完成
            subprocess.run(command, check=True)
            print(f"Successfully converted {filename} to markdown")
            
        except subprocess.CalledProcessError as e:
            print(f"Error converting {filename}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error while processing {filename}: {str(e)}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='Convert PDF files to Markdown using marker_single'
    )
    
    # 添加命令行参数
    parser.add_argument(
        '-i', '--input_dir',
        required=True,
        help='Directory containing PDF files to convert'
    )
    parser.add_argument(
        '-o', '--output_dir',
        required=True,
        help='Directory where converted Markdown files will be saved'
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行转换
    convert_pdfs_to_md(args.input_dir, args.output_dir)

if __name__ == '__main__':
    main()
