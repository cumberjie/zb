import re

# 假设你的直播源数据存储在 文件中
input_filename = '1.m3u'
output_filename = '2.m3u'

# 读取文件并处理数据
def process_live_sources(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        parts = line.strip().split(',')
        channel = parts[0].strip()
        url = parts[1].strip()
        bitrate_match = re.search(r'(\d+\.?\d*)M', parts[0])
        if bitrate_match:
            bitrate = bitrate_match.group(1)
            processed_line = f"{channel},{url}?\\$({bitrate})M"
            processed_lines.append(processed_line)

    # 对处理后的数据进行排序
    processed_lines.sort(key=lambda x: (x.split(',')[0], x.split('?\\$')[1].split('M')[0]))
    return processed_lines

# 分类处理后的数据
def classify_live_sources(processed_lines):
    categories = {
        'CCTV': [],
        'Satellite': [],
        'Other': []
    }
    for line in processed_lines:
        channel, url = line.split(',')
        channel = channel.upper()
        if channel.startswith('CCTV'):
            categories['CCTV'].append(line)
        elif '卫视' in channel:
            categories['Satellite'].append(line)
        else:
            categories['Other'].append(line)
    return categories

# 主函数
def main():
    processed_lines = process_live_sources(input_filename)
    
    # 打印排序后的数据
    print("Sorted Live Sources:")
    for line in processed_lines:
        print(line)
    
    # 打印分类后的数据并写入到文件
    print("\nClassified Live Sources:")
    categories = classify_live_sources(processed_lines)
    with open(output_filename, 'w') as file:  # 使用'w'模式覆盖文件
        for category, lines in categories.items():
            file.write(f"# {category}\n\n")
            for line in lines:
                file.write(line + "\n")

# 执行主函数
if __name__ == "__main__":
    main()
