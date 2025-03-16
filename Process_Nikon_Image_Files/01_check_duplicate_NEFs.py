import os
import exifread

def get_exif_signature(file_path):
    """提取EXIF关键特征"""
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
        # 组合关键EXIF特征
        signature = [
            str(tags.get('EXIF DateTimeOriginal', '')),
            str(tags.get('Image Make', '')),
            str(tags.get('Image Model', '')),
            str(tags.get('EXIF ExposureTime', ''))
        ]
        return '#'.join(signature)
    except Exception as e:
        print(f"读取EXIF失败: {file_path} - {str(e)}")
        return None

def find_duplicates(root_dir):
    """查找重复文件"""
    file_dict = {}
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if not file.lower().endswith('.nef'):
                continue
                
            file_path = os.path.join(root, file)
            exif_sig = get_exif_signature(file_path)
            
            if not exif_sig:
                continue  # 跳过读取失败的文件
                
            # 使用文件名和EXIF特征作为联合键
            compound_key = (file, exif_sig)
            
            if compound_key not in file_dict:
                file_dict[compound_key] = []
            file_dict[compound_key].append(file_path)
    
    # 返回有重复的条目
    return {k: v for k, v in file_dict.items() if len(v) > 1}

def save_results_to_file(duplicates, output_file):
    """将结果保存到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        if duplicates:
            f.write("发现重复文件：\n")
            for (filename, _), paths in duplicates.items():
                f.write(f"\n文件名: {filename}\n")
                f.write("重复路径：\n")
                for path in paths:
                    f.write(f"  - {path}\n")
        else:
            f.write("未发现重复文件\n")

if __name__ == '__main__':
    # target_dir = input("请输入要检查的目录路径：")
    target_dir="/mnt/c/Users/ysp/Qsync/00_Photos/Nikon_Z30" # access from wsl
    output_file = "results/duplicates.txt"  # 输出文件名
    duplicates = find_duplicates(target_dir)
    
    # 将结果保存到文件
    save_results_to_file(duplicates, output_file)
    print(f"结果已保存到文件: {output_file}")
