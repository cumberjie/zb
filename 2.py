import re 

# 自定义卫视排序规则
WEISHI_ORDER = [
    "广西卫视", "黑龙江卫视", "湖南卫视", "湖北卫视", "浙江卫视", 
    "江苏卫视", "河南卫视", "北京卫视", "东方卫视", "四川卫视", "广东卫视"
]

def parse_source(line):
    """解析每行内容，拆分出名称和URL"""
    # 将名称中的 `CCTV-数字 空格 文字` 格式处理为 `CCTV数字`
    def process_cctv_name(name):
        # 匹配 CCTV-数字 空格 文字 的结构并替换为 CCTV数字
        return re.sub(r'CCTV-(\d+\+?)\s*\S*', r'CCTV\1', name)

    parts = line.split(',', 1)
    name = parts[0].strip()
    url = parts[1].strip() if len(parts) > 1 else ''
    
    # 先处理名称中的 CCTV 格式
    name = process_cctv_name(name)
    
    # 提取质量 (带有M的部分)
    match = re.search(r"(\d+(\.\d+)?M)", name, re.IGNORECASE)
    quality = match.group(1).upper() if match else ''  # 提取带有M的部分并转换为大写
    
    # 处理干净的名称 (去掉质量信息)
    clean_name = re.sub(r"(\s*\d+(\.\d+)?M.*)", "", name, flags=re.IGNORECASE).strip()  # 去除质量信息的名称
    return clean_name, url, quality

def custom_sort_key(source):
    """定义排序规则"""
    name, _, quality = source
    
    # 央视区排序
    if name.upper().startswith("CCTV"):
        match = re.match(r"CCTV(\d+)", name.upper())
        number = int(match.group(1)) if match else float('inf')  # 提取数字
        return (0, number, -float(quality[:-1]) if quality else float('inf'))
    
    # 地区卫视区排序
    elif "卫视" in name:
        order_index = WEISHI_ORDER.index(name) if name in WEISHI_ORDER else len(WEISHI_ORDER)
        return (1, order_index, -float(quality[:-1]) if quality else float('inf'))
    
    # 其他排序
    else:
        return (2, name, -float(quality[:-1]) if quality else float('inf'))

def sort_sources(input_files, output_file):
    """读取、整理并输出结果"""
    # 读取所有文件，解析数据，并存储到一个列表中
    all_sources = []
    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        sources = [parse_source(line.strip()) for line in lines if line.strip()]
        # 去除重复的URL
        unique_sources = []
        seen_urls = set()
        for source in sources:
            name, url, quality = source
            if url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        all_sources.extend(unique_sources)
 
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
    input_files = ["99.m3u","by2.m3u"] # 输入文件
    output_file = "by9.m3u"  # 输出文件
    sort_sources(input_files, output_file)
    
