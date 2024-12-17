from pdfdeal.file_tools import auto_split_mds
from pathlib import Path

def split_markdown_files(output_dir: str):
    """拆分Markdown文件的段落"""
    print("\nStep 2: Splitting markdown files...")
    result = {
        'success': False,
        'success_files': [],
        'failed_files': [],
        'error': None
    }
    
    try:
        # 获取所有需要处理的markdown文件
        md_files = list(Path(output_dir).glob('*.md'))
        
        # 执行拆分操作
        success, failed, flag = auto_split_mds(
            mdpath=output_dir, 
            out_type="replace",
            split_str="=+=+=+=+=+=+=+=+="
        )
        
        # 记录处理结果
        result['success_files'].extend([str(f) for f in success])
        if flag:
            result['failed_files'].extend([str(f) for f in failed])
        
        result['success'] = len(result['failed_files']) == 0
        
        # 打印处理结果
        print(f"Split results - Success: {len(success)} files, Failed: {len(failed)}")
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        print(f"Error during markdown splitting: {e}")
    
    return result
