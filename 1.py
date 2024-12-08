import re

# 从GitHub仓库中读取原始数据文件
with open("1.m3u", "r", encoding="utf-8") as f:
    data = f.readlines()

# 排序函数
def custom_sort(entry):
    name, url = entry
    # 提取数字M部分
    match = re.search(r"(\d*\.?\d+)M", name)
    m_value = float(match.group(1)) if match else 0  # 如果没有数字M部分，默认为0
    return (name.replace("CCTV", ""), m_value)  # 排序依据为CCTV数字部分

# 整理后的数据列表
sorted_data = sorted(data, key=lambda entry: custom_sort(entry))

# 格式化输出
formatted_data = [f"{entry.split(' ')[0]},{entry.split(',')[1]}?${entry.split(' ')[1].replace('M', '')}" for entry in sorted_data]

# 分类函数
def categorize_and_sort(data):
    cctv = []
    regional = []
    others = []
    
    for entry in data:
        name, url = entry.split(",")
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
output_file = "11.m3u"
with open(output_file, 'w', encoding='utf-8') as f:
    for line in final_sorted_data:
        f.write(line + "\n")

print(f"数据已经写入到 {output_file} 文件中！")
