import os
from pathlib import Path
import subprocess
from pdfdeal.file_tools import auto_split_mds, mds_replace_imgs
from pdfdeal.FileTools.Img.PicGO import PicGO

def convert_and_preprocess(input_dir: str, output_dir: str, picgo_endpoint: str = "http://127.0.0.1:36677"):
    """
    将PDF转换为Markdown并进行RAG预处理
    
    Args:
        input_dir (str): PDF文件所在目录
        output_dir (str): 输出目录
        picgo_endpoint (str): PicGO服务器地址
    """
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Step 1: Converting PDFs to Markdown...")
    # 调用pdf2md.py进行转换
    try:
        subprocess.run([
            'python', 
            './ChunkConvertPDFtoMDbySeq/pdf2md.py',
            '-i', input_dir,
            '-o', output_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during PDF conversion: {e}")
        return
    
    print("\nStep 2: Splitting markdown files...")
    # 使用pdfdeal拆分段落
    try:
        success, failed, flag = auto_split_mds(
            mdpath=output_dir, 
            out_type="replace",  # 直接替换原文件
            split_str="=+=+=+=+=+=+=+=+="  # 使用默认分隔符
        )
        print(f"Split results - Success: {len(success)} files, Failed: {len(failed)}")
    except Exception as e:
        print(f"Error during markdown splitting: {e}")
        return

    print("\nStep 3: Uploading images via PicGO...")
    # 配置PicGO上传器
    try:
        picgo = PicGO(endpoint=picgo_endpoint)
        
        # 替换所有markdown文件中的图片为在线URL
        success, failed, flag = mds_replace_imgs(
            path=output_dir,
            replace=picgo,
            threads=5  # 使用5个线程进行上传
        )
        
        if flag:
            print("Warning: Some images failed to upload")
        print(f"Image upload results - Success: {len(success)} files, Failed: {len(failed)}")
        
        # 打印失败的文件信息
        if failed:
            print("\nFailed files:")
            for fail in failed:
                print(f"File: {fail.get('file', 'Unknown')}")
                print(f"Error: {fail.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"Error during image upload: {e}")
        return

    print("\nProcessing complete!")
    print(f"Processed files can be found in: {output_dir}")

def main():
    import argparse
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
    
    convert_and_preprocess(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        picgo_endpoint=args.picgo
    )

if __name__ == '__main__':
    main()
