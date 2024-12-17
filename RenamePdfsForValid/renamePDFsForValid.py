import os
import sys

def sanitize_filename(filename):
    """
    清理文件名，去除空格、'\'和'/'，将其替换为下划线
    """
    # 替换不允许的字符为下划线
    sanitized = filename.replace(' ', '_')
    sanitized = sanitized.replace('\\', '_')
    sanitized = sanitized.replace('/', '_')
    return sanitized

def rename_files_in_directory(directory):
    """
    递归遍历目录，重命名文件
    """
    try:
        # 遍历目录中的所有文件和子目录
        for root, dirs, files in os.walk(directory):
            for filename in files:
                # 获取完整的文件路径
                old_path = os.path.join(root, filename)
                
                # 获取新的文件名
                new_filename = sanitize_filename(filename)
                
                # 如果文件名发生变化，则进行重命名
                if new_filename != filename:
                    new_path = os.path.join(root, new_filename)
                    try:
                        os.rename(old_path, new_path)
                        print(f"重命名: {old_path} -> {new_path}")
                    except OSError as e:
                        print(f"重命名失败 {old_path}: {e}")
                        
    except Exception as e:
        print(f"处理目录时出错 {directory}: {e}")

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python renamePDFsForValid.py <directory_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # 检查目录是否存在
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是有效的目录")
        sys.exit(1)
    
    print(f"开始处理目录: {directory}")
    rename_files_in_directory(directory)
    print("处理完成")

if __name__ == "__main__":
    main()
