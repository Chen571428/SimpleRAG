from pdfdeal.file_tools import mds_replace_imgs
from pathlib import Path
from rate_limiter import RateLimiter

def process_images(output_dir: str, uploader, qps: int = 0):
    """
    处理并上传图片
    
    Args:
        output_dir: 输出目录
        uploader: 上传器函数或带有upload方法的对象
        qps: 每秒最大请求数，0表示不限制
    """
    print("\nStep 3: Uploading images...")
    result = {
        'success': False,
        'success_files': [],
        'failed_files': [],
        'error': None
    }
    
    try:
        # 获取所有需要处理的markdown文件
        md_files = list(Path(output_dir).glob('*.md'))
        
        # 如果设置了QPS限制，创建限流器并包装上传函数
        upload_func = uploader.upload_file if hasattr(uploader, 'upload_file') else uploader
        
        if qps > 0:
            rate_limiter = RateLimiter(qps)
            original_upload = upload_func
            
            def rate_limited_upload(*args, **kwargs):
                rate_limiter.acquire()
                return original_upload(*args, **kwargs)
            
            upload_func = rate_limited_upload
        
        # 替换图片
        success, failed, flag = mds_replace_imgs(
            path=output_dir,
            replace=upload_func,
            threads=2,
            down_load_threads=3,
            path_style=True,
            skip='https://'
        )
        
        # 记录处理结果
        result['success_files'].extend([str(f) for f in success])
        
        if failed:
            for fail in failed:
                file_info = {
                    'file': str(fail.get('file', 'Unknown')),
                    'error': str(fail.get('error', 'Unknown error'))
                }
                result['failed_files'].append(file_info)
        
        # 设置处理状态
        result['success'] = len(result['failed_files']) == 0
        
        # 打印处理结果
        if flag:
            print("Warning: Some images failed to upload")
        print(f"Image upload results - Success: {len(success)} files, Failed: {len(failed)}")
        
        # 打印失败详情
        if failed:
            print("\nFailed files:")
            for fail in failed:
                print(f"File: {fail.get('file', 'Unknown')}")
                print(f"Error: {fail.get('error', 'Unknown error')}")
                
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        print(f"Error during image upload: {e}")
    
    return result
