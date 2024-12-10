import re
from glob import glob

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

def merge_and_sort_sources(input_files, output_file):
    """读取多个文件，整理并输出结果"""
    all_lines = []
    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            all_lines.extend(file.readlines())
    
    # 解析数据
    sources = [parse_source(line.strip()) for line in all_lines if line.strip()]
    
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

if __name__ == "__main__":
    # 替换此路径为你的文件夹路径
    folder_path = "s"  # 指定文件夹路径

    # 读取所有文档
    input_files = glob.glob(f"{folder_path}/*")  # 或 glob.glob(f"{folder_path}/*.m3u") 只筛选 .m3u 文件

    if not input_files:
        print(f"文件夹 {folder_path} 中没有找到文件！")
    else:
        print(f"发现的文件: {input_files}")
        output_file = "s.m3u"  # 输出文件
        merge_and_sort_sources(input_files, output_file)
