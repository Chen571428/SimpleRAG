import subprocess
from pathlib import Path
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_conversion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def convert_pdf_to_md(input_dir: str, output_dir: str, converter='marker', process_each=False, uploader=None, qps=0, steps_to_run=None):
    """
    将PDF转换为Markdown文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        converter: 使用的转换器 ('marker' 或 'mineru')
        process_each: 是否对每个转换后的文件立即进行后续处理
        uploader: 图片上传器（当process_each=True且需要处理图片时需要）
        qps: 上传限速（当process_each=True且需要处理图片时可用）
        steps_to_run: 要运行的步骤列表
    """
    print(f"Step 1: Converting PDFs to Markdown using {converter}...")
    result = {
        'success': False,
        'success_files': [],
        'failed_files': [],
        'error': None
    }
    
    if steps_to_run is None:
        steps_to_run = [1, 2, 3]
    
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        pdf_files = list(input_path.glob('*.pdf'))
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file}")
            try:
                output_md = output_path / f"{pdf_file.stem}"
                print(f"Output path: {output_path}")
                
                if converter == 'marker':
                    command = [
                        'conda', 'run', '--no-capture-output', '-n', 'pdf2md',
                        'marker_single',
                        str(pdf_file),
                        '--output_dir', str(output_path),
                        '--output_format', 'markdown',
                        '--force_ocr'
                    ]
                else:  # mineru
                    output_md.mkdir(parents=True, exist_ok=True)
                    print(f"output_md: {output_md}")
                    command = [
                        'conda', 'run', '--no-capture-output', '-n', 'MinerU',
                        'magic-pdf',
                        '-p', str(pdf_file),
                        '-o', str(output_path),
                        '-m', 'ocr'  
                    ]
                
                subprocess.run(command)
                if converter == 'mineru':
                    output_file = output_md / f"ocr/{pdf_file.stem}.md"
                    output_file_img = output_md / f"ocr/images"

                    os.rename(output_file, output_md / f"{pdf_file.stem}.md")
                    os.rename(output_file_img, output_md / f"images")

                    output_last_path = output_md / "ocr"
                    print(f"output_last_path: {output_last_path}")
                    import shutil
                    shutil.rmtree(output_last_path, ignore_errors=True)
                
                result['success_files'].append(str(pdf_file))
                
                # 如果启用了即时处理，对刚转换的文件进行处理
                if process_each and output_md.exists():
                    from step2_split_md import split_markdown_files
                    from step3_process_images import process_images
                    print(f"Performing immediate processing for {pdf_file}")
                    
                    # 创建临时目录用于单文件处理
                    temp_dir = output_path / "temp_processing"
                    temp_dir.mkdir(exist_ok=True)
                    print(f"Created temp directory: {temp_dir}")
                    
                    # 复制文件到临时目录
                    temp_md = temp_dir / output_md.name
                    import shutil
                    shutil.copytree(output_md, temp_md)
                    
                    processed_file = temp_md
                    
                    # 根据选择的步骤执行处理
                    if 2 in steps_to_run:
                        print(f"Running step 2 (split) for {pdf_file}")
                        split_result = split_markdown_files(str(temp_dir))
                        if not split_result['success']:
                            print(f"Warning: Split failed for {pdf_file}")
                    
                    if 3 in steps_to_run:
                        print(f"Running step 3 (image processing) for {pdf_file}")
                        if uploader:
                            process_result = process_images(str(temp_dir), uploader, qps)
                            if not process_result['success']:
                                print(f"Warning: Image processing failed for {pdf_file}")
                    
                    # 处理完成，将处理后的文件移回原位置
                    shutil.rmtree(output_md, ignore_errors=True)  # 删除原目录
                    shutil.copytree(processed_file, output_md)
                    print(f"Moved processed file back to: {output_md}")
                    
                    # 清理临时目录
                    shutil.rmtree(temp_dir)
                    print(f"Cleaned up temp directory")
                
            except subprocess.CalledProcessError as e:
                result['failed_files'].append(str(pdf_file))
                error_msg = f"Error converting {pdf_file}: {e}"
                print(error_msg)
                logging.error(error_msg)
                continue
            except Exception as e:
                error_msg = f"Unexpected error processing {pdf_file}: {e}"
                print(error_msg)
                logging.error(error_msg)
                continue
        
        result['success'] = len(result['failed_files']) == 0
        summary_msg = f"\nProcessing completed. Successful: {len(result['success_files'])}, Failed: {len(result['failed_files'])}"
        print(summary_msg)
        logging.info(summary_msg)
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        error_msg = f"Fatal error: {e}"
        print(error_msg)
        logging.error(error_msg)
    
    return result
