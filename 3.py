import re
import os

# 自定义卫视排序规则
WEISHI_ORDER = [
    "广西卫视", "黑龙江卫视", "湖南卫视", "湖北卫视", "浙江卫视", 
    "江苏卫视", "河南卫视", "北京卫视", "东方卫视", "四川卫视", "广东卫视"
]

def parse_source(line):
    """解析每行内容，拆分出名称和URL"""
    def process_cctv_name(name):
        return re.sub(r'CCTV-(\d+\+?)\s*\S*', r'CCTV\1', name)

    parts = line.split(',', 1)
    name = parts[0].strip()
    url = parts[1].strip() if len(parts) > 1 else ''
    name = process_cctv_name(name)
    match = re.search(r"(\d+(\.\d+)?M)", name, re.IGNORECASE)
    quality = match.group(1).upper() if match else ''
    clean_name = re.sub(r"(\s*\d+(\.\d+)?M.*)", "", name, flags=re.IGNORECASE).strip()
    return clean_name, url, quality

def custom_sort_key(source):
    """定义排序规则"""
    name, _, quality = source
    if name.upper().startswith("CCTV"):
        match = re.match(r"CCTV(\d+)", name.upper())
        number = int(match.group(1)) if match else float('inf')
        return (0, number, -float(quality[:-1]) if quality else float('inf'))
    elif "卫视" in name:
        order_index = WEISHI_ORDER.index(name) if name in WEISHI_ORDER else len(WEISHI_ORDER)
        return (1, order_index, -float(quality[:-1]) if quality else float('inf'))
    else:
        return (2, name, -float(quality[:-1]) if quality else float('inf'))

def sort_sources(input_file, output_file):
    """读取、整理并输出结果"""
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # 解析数据
    sources = [parse_source(line.strip()) for line in lines if line.strip()]
    
    # 去除重复的URL
    unique_sources = []
    seen_urls = set()
    for source in sources:
        name, url, quality = source
        if url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(source)
    
    # 排序
    sorted_sources = sorted(unique_sources, key=custom_sort_key)
    
    # 按类别分组
    cctv_group = [source for source in sorted_sources if source[0].upper().startswith("CCTV")]
    weishi_group = [source for source in sorted_sources if "卫视" in source[0]]
    other_group = [source for source in sorted_sources if source not in cctv_group and source not in weishi_group]
    
    # 输出到文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("央视,#genre#\n")
        for name, url, quality in cctv_group:
            if quality:
                file.write(f"{name},{url}?${quality}\n")
            else:
                file.write(f"{name},{url}\n")
        
        file.write("\n卫视,#genre#\n")
        for name, url, quality in weishi_group:
            if quality:
                file.write(f"{name},{url}?${quality}\n")
            else:
                file.write(f"{name},{url}\n")
        
        file.write("\n其他,#genre#\n")
        for name, url, quality in other_group:
            if quality:
                file.write(f"{name},{url}?${quality}\n")
            else:
                file.write(f"{name},{url}\n")

# 新增的合并函数
def merge_and_sort_sources(input_files, output_file):
    """
    从多个文档抽取内容，合并处理并输出到一个文档。
    """
    if not input_files:
        print("未提供任何输入文件，操作终止。")
        return
    
    # 创建一个临时合并文件
    temp_file = "temp_combined_input.m3u"
    with open(temp_file, 'w', encoding='utf-8') as temp:
        for input_file in input_files:
            if os.path.exists(input_file):
                with open(input_file, 'r', encoding='utf-8') as file:
                    temp.writelines(file.readlines())
            else:
                print(f"文件 {input_file} 不存在，跳过。")
    
    # 调用原始的 sort_sources 方法对合并的文件处理
    sort_sources(temp_file, output_file)
    
    # 删除临时文件
    os.remove(temp_file)
    print(f"所有文件已合并并处理，输出到 {output_file}")

# 主函数
if __name__ == "__main__":
    file_paths = ["0.m3u", "by9.m3u"]        

    if not file_paths:
        print("未提供任何文档路径，程序终止。")
    else:
        output_file = "091.m3u"  # 输出文件
        merge_and_sort_sources(file_paths, output_file)
