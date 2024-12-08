import re

def parse_source(line):
    """解析每行内容，拆分出名称和URL"""
    parts = line.split(',', 1)
    name = parts[0].strip()
    url = parts[1].strip() if len(parts) > 1 else ''
    match = re.search(r"(\d+(\.\d+)?M)", name, re.IGNORECASE)
    quality = match.group(1).upper() if match else ''  # 提取带有M的部分并转换为大写
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
        return (1, name, -float(quality[:-1]) if quality else float('inf'))
    
    # 其他排序
    else:
        return (2, name, -float(quality[:-1]) if quality else float('inf'))

def sort_sources(input_file, output_file):
    """读取、整理并输出结果"""
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # 解析数据
    sources = [parse_source(line.strip()) for line in lines if line.strip()]
    
    # 排序
    sorted_sources = sorted(sources, key=custom_sort_key)
    
    # 重新组装数据并输出
    with open(output_file, 'w', encoding='utf-8') as file:
        for name, url, quality in sorted_sources:
            if quality:
                file.write(f"{name},{url}?${quality}\n")
            else:
                file.write(f"{name},{url}\n")

if __name__ == "__main__":
    input_file = "1.m3u"  # 输入文件
    output_file = "sorted_sources.txt"  # 输出文件
    sort_sources(input_file, output_file)
