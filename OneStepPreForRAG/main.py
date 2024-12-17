import argparse
from pathlib import Path
from step1_pdf_to_md import convert_pdf_to_md
from step2_split_md import split_markdown_files
from step3_process_images import process_images
from logger import ProcessLogger
from uploaders import UploaderFactory
from config import ConfigManager

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
    
    # 修改步骤选择参数，改用多选方式
    parser.add_argument(
        '--steps',
        type=int,
        nargs='+',
        choices=[1, 2, 3],
        help='Specify which steps to run (1: PDF to MD, 2: Split MD, 3: Process Images). Example: --steps 1 3'
    )
    
    # 上传器相关参数
    parser.add_argument(
        '--uploader',
        choices=['picgo', 'alioss'],
        default='picgo',
        help='Image uploader type (default: picgo)'
    )
    
    # PicGO参数
    parser.add_argument(
        '--picgo-endpoint',
        default="http://127.0.0.1:36677",
        help='PicGO server endpoint (default: http://127.0.0.1:36677)'
    )
    
    # 阿里云OSS参数
    parser.add_argument(
        '--oss-key-id',
        help='Aliyun OSS access key ID'
    )
    parser.add_argument(
        '--oss-key-secret',
        help='Aliyun OSS access key secret'
    )
    parser.add_argument(
        '--oss-endpoint',
        help='Aliyun OSS endpoint'
    )
    parser.add_argument(
        '--oss-bucket',
        help='Aliyun OSS bucket name'
    )
    
    # 添加配置文件参数
    parser.add_argument(
        '--config',
        help='Path to config file (default: search in current directory and user home)'
    )
    
    # 添加创建配置模板的参数
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create a default config file in current directory'
    )
    
    # 添加QPS限制参数
    parser.add_argument(
        '--qps',
        type=int,
        default=0,
        help='Maximum queries per second for image upload (0 for no limit)'
    )
    
    # 在参数部分添加新的选项
    parser.add_argument(
        '--process-each',
        action='store_true',
        help='Process each PDF file immediately after conversion'
    )
    
    # 在main.py的参数部分添加：
    parser.add_argument(
        '--converter',
        choices=['marker', 'mineru'],
        default='marker',
        help='PDF to Markdown converter to use (default: marker)'
    )
    
    args = parser.parse_args()
    
    # 如果请求创建配置模板
    if args.create_config:
        ConfigManager.create_default_config()
        return
    
    # 确保输出目录存在
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化日志记录器
    process_logger = ProcessLogger(args.output_dir)
    
    try:
        # 加载配置
        config_manager = ConfigManager(args.config)
        
        # 创建上传器（仅在需要时）
        uploader = None
        if args.steps is None or 3 in args.steps or args.process_each:
            uploader_params = {}
            if args.uploader == 'picgo':
                # 优先使用命令行参数，如果没有则使用配置文件
                picgo_config = config_manager.get_uploader_config('picgo')
                uploader_params['endpoint'] = args.picgo_endpoint or picgo_config.get('endpoint')
                
            elif args.uploader == 'alioss':
                # 优先使用命令行参数，如果没有则使用配置文件
                oss_config = config_manager.get_uploader_config('alioss')
                uploader_params.update({
                    'access_key_id': args.oss_key_id or oss_config.get('access_key_id'),
                    'access_key_secret': args.oss_key_secret or oss_config.get('access_key_secret'),
                    'endpoint': args.oss_endpoint or oss_config.get('endpoint'),
                    'bucket': args.oss_bucket or oss_config.get('bucket')
                })
                
                # 验证所有必需的参数都已提供
                if not all(uploader_params.values()):
                    raise ValueError("Missing required OSS parameters in both command line and config file")
            
            uploader = UploaderFactory.create_uploader(args.uploader, **uploader_params)
        
        # 确定要运行的步骤
        steps_to_run = args.steps if args.steps else [1, 2, 3]
        
        if 1 in steps_to_run:
            # 执行步骤1：PDF转MD
            step1_result = convert_pdf_to_md(
                args.input_dir, 
                args.output_dir,
                converter=args.converter,
                process_each=args.process_each,
                uploader=uploader if args.process_each else None,
                qps=args.qps if args.process_each else 0,
                steps_to_run=steps_to_run
            )
            process_logger.log_step_result(
                'pdf_to_md',
                step1_result['success_files'],
                step1_result['failed_files'],
                step1_result.get('error')
            )
            if not step1_result['success']:
                process_logger.finalize('failed at step 1')
                return
            
            # 如果启用了即时处理，跳过后续的批量处理步骤
            if args.process_each:
                process_logger.finalize('completed with individual processing')
                return
        
        if 2 in steps_to_run:
            # 执行步骤2：拆分MD文件
            step2_result = split_markdown_files(args.output_dir)
            process_logger.log_step_result(
                'split_md',
                step2_result['success_files'],
                step2_result['failed_files'],
                step2_result.get('error')
            )
            if not step2_result['success']:
                process_logger.finalize('failed at step 2')
                return
        
        if 3 in steps_to_run:
            # 执行步骤3：处理图片
            step3_result = process_images(args.output_dir, uploader, args.qps)
            process_logger.log_step_result(
                'process_images',
                step3_result['success_files'],
                step3_result['failed_files'],
                step3_result.get('error')
            )
            if not step3_result['success']:
                process_logger.finalize('failed at step 3')
                return
        
        # 完成处理
        steps_str = ', '.join(map(str, steps_to_run))
        status = f"completed steps: {steps_str}"
        process_logger.finalize(status)
        print(f"\nProcessing {status}!")
        print(f"Processed files can be found in: {args.output_dir}")
        print(f"Processing logs and summary can be found in: {args.output_dir}/logs")
        
    except Exception as e:
        process_logger.finalize(f'failed with error: {str(e)}')
        print(f"Error: {e}")

if __name__ == '__main__':
    main()