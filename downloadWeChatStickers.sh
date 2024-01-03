#!/bin/bash

# 定义 plist 文件的路径
plist_path="/Users/Eros/Downloads/fav.archive.plist"

# 读取 plist 文件，并使用 grep 提取所有的 http 链接
links=$(defaults read "$plist_path" | grep -o 'http[^ ]*')

# 获取当前日期和时间作为目录名
dir_name=$(date "+%Y%m%d-%H%M%S")

# 在 Downloads 目录中创建新的子目录
mkdir -p ~/Downloads/"$dir_name"

# 切换到新创建的子目录
cd ~/Downloads/"$dir_name"

# 初始化文件名计数器
counter=1

# 下载每个链接
for link in $links; do
    # 使用计数器作为文件名并添加 .jpg 后缀
    file_name="${counter}.jpg"
    echo "正在下载: $link"
    curl -o "$file_name" "$link"
    
    # 增加计数器
    ((counter++))
done

echo "所有文件下载完成。"
