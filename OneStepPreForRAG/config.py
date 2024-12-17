import json
from pathlib import Path
import os

class ConfigManager:
    def __init__(self, config_path=None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则寻找默认位置
        """
        if config_path is None:
            # 查找默认配置文件位置
            default_locations = [
                Path.cwd() / 'config.json',  # 当前目录
                Path.home() / '.pdfdeal' / 'config.json',  # 用户目录
            ]
            
            for loc in default_locations:
                if loc.exists():
                    self.config_path = loc
                    break
            else:
                raise FileNotFoundError(
                    "No config file found. Please create config.json or specify config path. "
                    "You can use config.template.json as a template."
                )
        else:
            self.config_path = Path(config_path)
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # 读取配置文件
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def get_uploader_config(self, uploader_type: str) -> dict:
        """
        获取指定上传器的配置
        
        Args:
            uploader_type: 上传器类型 ('alioss' 或 'picgo')
        
        Returns:
            dict: 上传器配置参数
        """
        if uploader_type not in self.config:
            raise ValueError(f"No configuration found for uploader: {uploader_type}")
        
        return self.config[uploader_type]
    
    @staticmethod
    def create_default_config(output_path: Path = None):
        """
        创建默认配置文件
        
        Args:
            output_path: 输出路径，如果为None则在当前目录创建
        """
        if output_path is None:
            output_path = Path.cwd() / 'config.json'
        
        template_path = Path(__file__).parent / 'config.template.json'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
            
            print(f"Created default config file at: {output_path}")
        else:
            raise FileNotFoundError("Template config file not found") 