#!/bin/bash
# exit when any command fails
set -e
extractDir=$1
current_dir=$(pwd)

while getopts ":d:e:i" opt; do
  case $opt in
    d) # 当前要执行的完整目录地址
      extractDir="$OPTARG"
      ;;
    e) # 设置提取的特定字符串，只提取包含此字符串的文件
      extractContains="$OPTARG"
      ;;
    i) # 设定需要忽略的字符串，包含此字符串时会进行忽略
      ignoreContains="$OPTARG"
      ;;
    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done

if [ -z "$extractDir" ]; then
  echo "执行脚本时请带上主目录路径"
  exit 2
fi

echo "============================="
echo "开始提取主目录：$extractDir"
echo ""

cd $extractDir

for file in *; do
  filePath=$extractDir"/"$file
  if [ -d "$filePath" ]; then
    $current_dir/unzipAndExtractImage.sh -d "$filePath" -e "$extractContains" -i "$ignoreContains"
  fi
done

echo ""
echo "完成提取主目录：$extractDir"
echo "============================="
