import os
import hashlib
from pathlib import Path
from collections import defaultdict
import argparse

def calculate_md5(file_path):
    """计算文件的MD5值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicates(directory, dry_run=True):
    """
    递归检查目录下的所有文件，移除重复文件
    
    Args:
        directory: 要检查的目录路径
        dry_run: 如果为True，只显示要删除的文件而不实际删除
    """
    # 用于存储MD5到文件路径的映射
    md5_map = defaultdict(list)
    
    # 递归遍历目录
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            try:
                file_md5 = calculate_md5(file_path)
                md5_map[file_md5].append(file_path)
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
    
    # 统计信息
    total_files = sum(len(files) for files in md5_map.values())
    duplicate_files = sum(len(files) - 1 for files in md5_map.values() if len(files) > 1)
    saved_space = 0
    
    # 处理重复文件
    for md5, files in md5_map.items():
        if len(files) > 1:
            # 保留第一个文件，删除其余的
            original = files[0]
            duplicates = files[1:]
            
            print(f"\n发现重复文件 (MD5: {md5}):")
            print(f"保留: {original}")
            print("删除:")
            for dup in duplicates:
                saved_space += dup.stat().st_size
                print(f"- {dup}")
                if not dry_run:
                    try:
                        os.remove(dup)
                    except Exception as e:
                        print(f"删除文件 {dup} 时出错: {e}")
    
    # 打印统计信息
    print(f"\n统计信息:")
    print(f"总文件数: {total_files}")
    print(f"重复文件数: {duplicate_files}")
    print(f"可节省空间: {saved_space / (1024*1024):.2f} MB")
    
    if dry_run:
        print("\n这是演示模式，没有实际删除文件。")
        print("要实际删除文件，请使用 --force 参数运行脚本。")

def main():
    parser = argparse.ArgumentParser(description='删除重复文件，只保留一份')
    parser.add_argument('directory', help='要检查的目录路径')
    parser.add_argument('--force', action='store_true', help='实际删除文件（默认只显示）')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"错误：{args.directory} 不是有效的目录")
        return
    
    remove_duplicates(args.directory, dry_run=not args.force)

if __name__ == '__main__':
    main()
