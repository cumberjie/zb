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

    # 处理名称中的CCTV和数字部分，提取出数字
    cctv_match = re.match(r"CCTV(\d+)", name.strip().upper())
    if cctv_match:
        cctv_number = int(cctv_match.group(1))  # 获取CCTV后的数字
    else:
        cctv_number = float('inf')  # 非CCTV条目排序到最后

    # 提取数字M部分（如有）
    m_match = re.search(r"(\d*\.?\d+)M", name)
    m_value = float(m_match.group(1)) if m_match else 0  # 如果没有数字M部分，默认为0

    return (cctv_number, m_value)

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
        
        # 提取数字M部分并确保格式统一
        m_value = re.search(r"(\d*\.?\d+)M", name)  # 查找数字M部分
        if m_value:
            m_value = m_value.group(1)  # 提取数字
            formatted_entry = f"{name.split()[0]},{url}?${m_value}M"  # 保持CCTV名称部分并添加M
        else:
            formatted_entry = f"{name.split()[0]},{url}?$0M"  # 没有M部分的添加$0M
        
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
    
    # 对每个类别内部进行排序，确保数字M大的排在前面，数字M为0的排在后面
    def sort_key(entry):
        name, url = entry.split(",", 1)
        m_value = re.search(r"(\d*\.?\d+)M", name)
        m_value = float(m_value.group(1)) if m_value else 0
        return -m_value  # 排序时数字大的排前面，0排后面

    cctv_sorted = sorted(cctv, key=sort_key)
    regional_sorted = sorted(regional, key=sort_key)
    others_sorted = sorted(others, key=lambda x: x.split(",")[0])  # 对“其他”类别按名称字母排序
    
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
