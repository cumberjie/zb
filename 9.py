import re

# 读取文件
with open("9.m3u", "r", encoding="utf-8") as file:
    content = file.read()

# 替换IPv6地址
updated_content = re.sub(r'\[.*?\]', '', content)

# 保存修改后的文件
with open("99.m3u", "w", encoding="utf-8") as file:
    file.write(updated_content)

print("IPv6 地址已移除并保存到 output.txt")
