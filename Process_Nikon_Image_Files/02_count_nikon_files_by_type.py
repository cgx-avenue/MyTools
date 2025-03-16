import os

def count_files_by_type(root_dir):
    # 分别统计nef和jpg文件的数量
    result = {}
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            nef_count = 0
            jpg_count = 0
            for file_entry in os.scandir(entry.path):
                if file_entry.is_file():
                    if file_entry.name.lower().endswith('.nef'):
                        nef_count += 1
                    elif file_entry.name.lower().endswith('.jpg'):
                        jpg_count += 1
            result[entry.name] = {'NEF': nef_count, 'JPG': jpg_count}
    return result


def save_results_to_file(file_counts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("子文件夹文件数量统计（仅.NEF和.JPG）：\n")
        for folder, count in file_counts.items():
            f.write(f"{folder}: {count} 个文件\n")



if __name__ == '__main__':
    # target_dir = input("请输入要检查的目录路径：")
    target_dir="/mnt/c/Users/ysp/Qsync/00_Photos/Nikon_Z30"
    file_counts = count_files_by_type(target_dir)
    
    if file_counts:
        save_results_to_file(file_counts,"results/count_nikon_files.txt")
        print("子文件夹文件数量统计（仅.NEF和.JPG）：")
        for folder, count in file_counts.items():
            print(f"{folder}: {count} 个文件")
    else:
        print("未发现子文件夹")
