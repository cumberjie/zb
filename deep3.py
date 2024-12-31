import re
import os

# 定义卫视排序顺序
WEISHI_ORDER = [
    "广西卫视", "黑龙江卫视", "湖南卫视", "湖北卫视", "浙江卫视", 
    "江苏卫视", "河南卫视", "北京卫视", "东方卫视", "四川卫视", "广东卫视"
]

def process_cctv_name(name):
    """处理CCTV名称，去除多余的字符"""
    return re.sub(r'CCTV-(\d+\+?)\s*\S*', r'CCTV\1', name)

def parse_source(line):
    """解析每行内容，拆分出名称、URL和质量"""
    name, url = line.strip().split(',', 1)
    name = process_cctv_name(name)
    quality_match = re.search(r"(\d+(\.\d+)?M)", name, re.IGNORECASE)
    quality = quality_match.group(1).upper() if quality_match else ''
    clean_name = re.sub(r"(\s*\d+(\.\d+)?M.*)", "", name, flags=re.IGNORECASE).strip()
    return clean_name, url.strip(), quality

def get_sort_key(source):
    """获取排序键"""
    name, _, quality = source
    if name.upper().startswith("CCTV"):
        number = int(re.match(r"CCTV(\d+)", name.upper()).group(1))
        return (0, number, -float(quality[:-1]) if quality else float('inf'))
    elif "卫视" in name:
        order_index = WEISHI_ORDER.index(name) if name in WEISHI_ORDER else len(WEISHI_ORDER)
        return (1, order_index, -float(quality[:-1]) if quality else float('inf'))
    else:
        return (2, name, -float(quality[:-1]) if quality else float('inf'))

def sort_sources(input_file, output_file):
    """读取、整理并输出结果"""
    # 解析数据
    with open(input_file, 'r', encoding='utf-8') as file:
        sources = [parse_source(line) for line in file if line.strip()]
    
    # 去除重复的URL
    unique_sources = {}
    for name, url, quality in sources:
        if url not in unique_sources:
            unique_sources[url] = (name, url, quality)
    
    # 排序
    sorted_sources = sorted(unique_sources.values(), key=get_sort_key)
    
    # 按类别分组
    cctv_group = [source for source in sorted_sources if source[0].upper().startswith("CCTV")]
    weishi_group = [source for source in sorted_sources if "卫视" in source[0]]
    other_group = [source for source in sorted_sources if source not in cctv_group and source not in weishi_group]
    
    # 输出到文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("央视,#genre#\n")
        for name, url, quality in cctv_group:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        file.write("\n卫视,#genre#\n")
        for name, url, quality in weishi_group:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        file.write("\n其他,#genre#\n")
        for name, url, quality in other_group:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")

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
    
    # 调用sort_sources方法对合并的文件处理
    sort_sources(temp_file, output_file)
    
    # 删除临时文件
    os.remove(temp_file)
    print(f"所有文件已合并并处理，输出到 {output_file}")

if __name__ == "__main__":
    file_paths = ["0.m3u", "99.m3u", "by.m3u"]        
    if not file_paths:
        print("未提供任何文档路径，程序终止。")
    else:
        output_file = "0921.m3u"  # 输出文件
        merge_and_sort_sources(file_paths, output_file)
        print(output_file)
