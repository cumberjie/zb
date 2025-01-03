import re
import os

WEISHI_ORDER = [
    "广西卫视", "黑龙江卫视", "湖南卫视", "湖北卫视", "浙江卫视", 
    "江苏卫视", "河南卫视", "北京卫视", "东方卫视", "四川卫视", "广东卫视"
]

def parse_source(line):
    """解析名称和URL"""
    name, _, url = line.partition(',')
    name = re.sub(r'CCTV-(\d+\+?)\s*\S*', r'CCTV\1', name.strip())
    quality = (re.search(r"(\d+(\.\d+)?M)", name, re.IGNORECASE) or [None, ""])[1].upper()
    clean_name = re.sub(r"\s*\d+(\.\d+)?M.*", "", name, flags=re.IGNORECASE).strip()
    return clean_name, url.strip(), quality

def custom_sort_key(source):
    """定义排序规则"""
    name, _, quality = source
    if name.startswith("CCTV"):
        number = int(re.search(r"CCTV(\d+)", name).group(1)) if re.search(r"CCTV(\d+)", name) else float('inf')
        return (0, number, -float(quality[:-1]) if quality else float('inf'))
    elif "卫视" in name:
        order_index = WEISHI_ORDER.index(name) if name in WEISHI_ORDER else len(WEISHI_ORDER)
        return (1, order_index, -float(quality[:-1]) if quality else float('inf'))
    elif name.startswith("本地") or re.match(r"精品\d+", name):
        # 本地和精品分类不参与整体排序
        return (4, name, -float(quality[:-1]) if quality else float('inf'))
    return (2, name, -float(quality[:-1]) if quality else float('inf'))

def sort_and_write_sources(sources, output_file):
    """对源进行排序并写入文件"""
    # 分类并排序
    cctv_sources = sorted([source for source in sources if source[0].startswith("CCTV")], key=custom_sort_key)
    weishi_sources = sorted([source for source in sources if "卫视" in source[0]], key=custom_sort_key)
    local_sources = [source for source in sources if source[0].startswith("本地")]
    fine_sources = {}
    for source in sources:
        if re.match(r"精品\d+", source[0]):
            if source[0] not in fine_sources:
                fine_sources[source[0]] = []
            fine_sources[source[0]].append(source)
    other_sources = sorted([source for source in sources if not source[0].startswith("CCTV") and "卫视" not in source[0] and not source[0].startswith("本地") and not re.match(r"精品\d+", source[0])], key=custom_sort_key)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("央视,#genre#\n")
        for name, url, quality in cctv_sources:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        file.write("\n卫视,#genre#\n")
        for name, url, quality in weishi_sources:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        file.write("\n本地,#genre#\n")
        for name, url, quality in sorted(local_sources, key=lambda x: x[0]):
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        for fine_name, group in fine_sources.items():
            file.write(f"\n{fine_name},#genre#\n")
            for name, url, quality in sorted(group, key=lambda x: x[0]):
                file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")
        
        file.write("\n其他,#genre#\n")
        for name, url, quality in other_sources:
            file.write(f"{name},{url}?${quality}\n" if quality else f"{name},{url}\n")

def merge_and_sort_sources(input_files, output_file):
    """合并并排序多个文件"""
    sources = []
    for input_file in input_files:
        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as file:
                sources.extend(parse_source(line.strip()) for line in file if line.strip())
    
    sort_and_write_sources(sources, output_file)

if __name__ == "__main__":
    file_paths = ["0.m3u", "by.m3u"]
    if file_paths:
        merge_and_sort_sources(file_paths, "091.m3u")
