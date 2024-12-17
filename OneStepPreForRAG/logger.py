import logging
from pathlib import Path
from datetime import datetime
import json

class ProcessLogger:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.log_dir = self.output_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"process_{self.timestamp}.log"
        self.summary_file = self.log_dir / f"summary_{self.timestamp}.json"
        
        # 初始化日志记录器
        self.logger = logging.getLogger(f"process_{self.timestamp}")
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 初始化处理结果
        self.results = {
            "start_time": datetime.now().isoformat(),
            "steps": {
                "pdf_to_md": {"status": "pending", "success": [], "failed": []},
                "split_md": {"status": "pending", "success": [], "failed": []},
                "process_images": {"status": "pending", "success": [], "failed": []}
            },
            "end_time": None,
            "overall_status": "pending"
        }
    
    def log_step_result(self, step_name, success_files, failed_files, error=None):
        """记录每个步骤的结果"""
        self.results["steps"][step_name]["status"] = "completed" if not failed_files else "failed"
        self.results["steps"][step_name]["success"] = success_files
        self.results["steps"][step_name]["failed"] = failed_files
        if error:
            self.results["steps"][step_name]["error"] = str(error)
        
        # 记录日志
        self.logger.info(f"Step {step_name} completed")
        self.logger.info(f"Success: {len(success_files)} files")
        self.logger.info(f"Failed: {len(failed_files)} files")
        if failed_files:
            self.logger.warning(f"Failed files in {step_name}:")
            for f in failed_files:
                self.logger.warning(f"  - {f}")
    
    def finalize(self, overall_status):
        """完成处理并生成总结"""
        self.results["end_time"] = datetime.now().isoformat()
        self.results["overall_status"] = overall_status
        
        # 写入总结文件
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 生成人类可读的总结
        self.generate_readable_summary()
    
    def generate_readable_summary(self):
        """生成人类可读的总结文件"""
        summary_txt = self.log_dir / f"summary_{self.timestamp}.txt"
        
        with open(summary_txt, 'w', encoding='utf-8') as f:
            f.write("处理总结\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"开始时间: {self.results['start_time']}\n")
            f.write(f"结束时间: {self.results['end_time']}\n")
            f.write(f"总体状态: {self.results['overall_status']}\n\n")
            
            for step, result in self.results["steps"].items():
                f.write(f"\n{step} 步骤结果:\n")
                f.write("-"*30 + "\n")
                f.write(f"状态: {result['status']}\n")
                f.write(f"成功文件数: {len(result['success'])}\n")
                f.write(f"失败文件数: {len(result['failed'])}\n")
                
                if result['failed']:
                    f.write("\n失败的文件:\n")
                    for file in result['failed']:
                        f.write(f"  - {file}\n")
                
                if 'error' in result:
                    f.write(f"\n错误信息: {result['error']}\n")
                
                f.write("\n")
