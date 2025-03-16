import os
import hashlib
from collections import defaultdict
from tqdm import tqdm
import time

def calculate_file_hash(file_path, chunk_size=8192):
    """计算文件哈希值（MD5）"""
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"\n哈希计算失败: {file_path} - {str(e)}")
        return None



def collect_files_with_metadata(root_dir):
    """收集文件元数据并显示进度条"""
    file_db = defaultdict(lambda: {'NEF': [], 'JPG': []})
    
    # 先收集所有文件路径
    all_files = []
    for root, _, files in os.walk(root_dir):
        all_files.extend((root, f) for f in files)
    
    # 使用进度条处理
    with tqdm(total=len(all_files), desc="扫描文件", unit="file") as pbar:
        for root, file in all_files:
            file_lower = file.lower()
            base_name = os.path.splitext(file)[0].lower()
            ext = os.path.splitext(file)[1].lower()
            full_path = os.path.join(root, file)
            
            try:
                # 获取文件修改时间
                mtime = os.path.getmtime(full_path)
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                
                # 使用文件名基+时间作为联合键
                compound_key = (base_name, time_str)
                
                if ext == '.nef':
                    file_db[compound_key]['NEF'].append(full_path)
                elif ext == '.jpg':
                    file_db[compound_key]['JPG'].append(full_path)
                    
            except Exception as e:
                print(f"\n文件处理失败: {full_path} - {str(e)}")
            
            pbar.update(1)
    
    return file_db
def generate_html_report(duplicates, output_file):
    """生成交互式HTML报告"""
    html_template = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>重复文件分析报告</title>
        <style>
            .duplicate-group {{ 
                margin: 20px 0; 
                padding: 15px; 
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .collapsible {{
                background-color: #f0f8ff;
                padding: 12px;
                cursor: pointer;
                font-weight: bold;
            }}
            .content {{ 
                display: none; 
                padding: 10px;
                background-color: #f9f9f9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                text-align: left;
            }}
            td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{background-color: #f5f5f5;}}
        </style>
    </head>
    <body>
        <h1>重复文件分析报告</h1>
        <p>发现 {} 组重复文件</p>
        {}
    </body>
    </html>"""
    
    group_template = """
    <div class="duplicate-group">
        <div class="collapsible" onclick="toggleGroup(this)">
            文件名基：{base_name} | 时间：{time_str}
        </div>
        <div class="content">
            <h3>NEF 文件（共 {nef_count} 个）</h3>
            <table>
                <tr><th>文件路径</th></tr>
                {nef_rows}
            </table>
            
            <h3>JPG 文件（共 {jpg_count} 个）</h3>
            <table>
                <tr><th>文件路径</th></tr>
                {jpg_rows}
            </table>
        </div>
    </div>
    """
    
    script = """
    <script>
    function toggleGroup(element) {
        const content = element.nextElementSibling;
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
    </script>
    """
    
    groups = []
    for (base_name, time_str), files in duplicates.items():
        # 生成表格行
        nef_rows = "\n".join(
            f"<tr><td>{path}</td></tr>" 
            for path in files['NEF']
        )
        jpg_rows = "\n".join(
            f"<tr><td>{path}</td></tr>" 
            for path in files['JPG']
        )
        
        groups.append(group_template.format(
            base_name=base_name,
            time_str=time_str,
            nef_count=len(files['NEF']),
            nef_rows=nef_rows,
            jpg_count=len(files['JPG']),
            jpg_rows=jpg_rows
        ))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template.format(
            len(duplicates),
            "\n".join(groups) + script
        ))

def analyze_duplicates(file_db):
    """分析重复文件"""
    duplicates = {}
    
    for base_name, files in file_db.items():
        # 需要同时存在两种格式
        if not files['NEF'] or not files['JPG']:
            continue
        
        # 记录所有文件
        duplicates[base_name] = files
    
    return duplicates

if __name__ == '__main__':
    # target_dir = input("请输入要扫描的目录路径：")
    target_dir="/mnt/c/Users/ysp/Qsync/00_Photos/Nikon_Z30"

    output_html = "results/duplicates_report.html"
    
    # 收集文件数据
    file_database = collect_files_with_metadata(target_dir)
    
    # 分析重复项
    print("\n分析重复文件...")
    duplicate_files = analyze_duplicates(file_database)
    
    # 生成报告
    print("生成可视化报告...")
    generate_html_report(duplicate_files, output_html)
    
    print(f"操作完成，报告已保存至：{output_html}")
