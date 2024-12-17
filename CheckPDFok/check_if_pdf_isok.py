import os
import shutil
from PyPDF2 import PdfReader
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='pdf_check.log'
    )

def check_pdf(file_path):
    """检查PDF文件是否可以正常打开"""
    try:
        with open(file_path, 'rb') as file:
            PdfReader(file)
        return True
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return False

def process_single_pdf(file_info, source_dir, good_dir, bad_dir):
    """处理单个PDF文件"""
    root, file = file_info
    pdf_path = os.path.join(root, file)
    
    # 检查PDF是否正常
    is_good = check_pdf(pdf_path)
    
    # 确定目标路径
    relative_path = os.path.relpath(root, source_dir)
    if is_good:
        target_dir = os.path.join(good_dir, relative_path)
    else:
        target_dir = os.path.join(bad_dir, relative_path)
    
    # 创建目标子目录
    os.makedirs(target_dir, exist_ok=True)
    
    # 复制文件
    target_path = os.path.join(target_dir, file)
    try:
        shutil.copy2(pdf_path, target_path)
        status = "good" if is_good else "bad"
        logging.info(f"Copied {file} to {status} folder")
        return True
    except Exception as e:
        logging.error(f"Error copying {file}: {str(e)}")
        return False

def process_pdfs(source_dir, good_dir, bad_dir):
    """并发处理目录下的所有PDF文件"""
    # 创建目标目录（如果不存在）
    os.makedirs(good_dir, exist_ok=True)
    os.makedirs(bad_dir, exist_ok=True)

    # 收集所有PDF文件
    pdf_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append((root, file))

    # 创建偏函数，固定某些参数
    process_func = partial(process_single_pdf, 
                         source_dir=source_dir, 
                         good_dir=good_dir, 
                         bad_dir=bad_dir)

    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        # 提交所有任务
        future_to_file = {executor.submit(process_func, pdf_file): pdf_file 
                         for pdf_file in pdf_files}
        
        # 等待所有任务完成
        for future in as_completed(future_to_file):
            file_info = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing {file_info[1]}: {str(e)}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='检查PDF文件完整性并分类')
    parser.add_argument('source_dir', help='源PDF文件目录路径')
    parser.add_argument('good_dir', help='正常PDF存放目录路径')
    parser.add_argument('bad_dir', help='损坏PDF存放目录路径')
    
    args = parser.parse_args()

    # 设置日志
    setup_logging()

    # 处理PDF文件
    logging.info("Starting PDF processing...")
    process_pdfs(args.source_dir, args.good_dir, args.bad_dir)
    logging.info("PDF processing completed")

if __name__ == "__main__":
    main()
