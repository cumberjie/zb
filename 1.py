import re

# 读取原始数据文件
with open("1.m3u", "r", encoding="utf-8") as f:
    data = f.readlines()

# 排序函数
def custom_sort(entry):
    # 确保条目格式正确，避免出现没有逗号的情况
    try:
        name, url = entry.split(',')
    except ValueError:
        return None  # 如果数据格式不正确，返回None

    # 提取数字M部分
    match = re.search(r"(\d*\.?\d+)M", name)
    m_value = float(match.group(1)) if match else 0  # 如果没有数字M部分，默认为0
    return (name.replace("CCTV", ""), m_value)  # 排序依据为CCTV数字部分

# 过滤掉无效的条目
valid_data = [entry for entry in data if custom_sort(entry) is not None]

# 排序后的数据
sorted_data = sorted(valid_data, key=lambda entry: custom_sort(entry))

# 格式化输出，确保每个条目都符合要求
formatted_data = []
for entry in sorted_data:
    parts = entry.split(',')
    
    # 确保数据有足够的部分
    if len(parts) >= 2:
        name = parts[0].strip()
        url = parts[1].strip()
        # 处理数字M部分
        m_value = name.split(' ')[-1].replace('M', '') if 'M' in name else '0'
        formatted_entry = f"{name},{url}?${m_value}"
        formatted_data.append(formatted_entry)

# 分类函数
def categorize_and_sort(data):
    cctv = []
    regional = []
    others = []
    
    for entry in data:
        name, url = entry.split(",", 1)  # 确保只按第一个逗号分割
        name = name.upper()  # 不区分大小写，统一转为大写
        if "CCTV" in name:
            cctv.append(entry)
        elif "卫视" in name:
            regional.append(entry)
        else:
            others.append(entry)
    
    # 对每个类别内部进行排序
    cctv_sorted = sorted(cctv, key=custom_sort)
    regional_sorted = sorted(regional, key=custom_sort)
    others_sorted = sorted(others, key=lambda x: x.split(",")[0])
    
    # 合并所有分类后的数据
    return cctv_sorted + regional_sorted + others_sorted

# 分类并排序数据
final_sorted_data = categorize_and_sort(formatted_data)

# 将最终结果输出到新的文本文件
output_file = "sorted_live_streams.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    for line in final_sorted_data:
        f.write(line + "\n")

print(f"数据已经写入到 {output_file} 文件中！")
