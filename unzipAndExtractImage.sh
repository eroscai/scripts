#!/bin/bash
# exit when any command fails
set -e

usage() { echo "$0 usage:" && grep " .)\ #" $0; exit 0; }
[ $# -eq 0 ] && usage

while getopts ":d:e:i:f" opt; do
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
    f) # 设定需要过滤的内嵌文件夹，包含此字符串时会进行忽略 eg：./unzipAndExtractImage.sh -d 目标路径 -f 过滤文件夹字符串
      filterFolderContains="$OPTARG"
      ;;
    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done

if [ -z "$extractDir" ]; then
  echo "执行脚本时请带上目录路径"
  exit 2
fi

echo "============================="
echo "开始提取目录："$extractDir""

isImage() {
  fileName="$(basename "$1")"
  extension="${fileName##*.}"
  if [[ $extension == "jpg" ]] || [[ $extension == "png" ]]; then
    true
  else
    false
  fi
}

isZip() {
  fileName="$(basename "$1")"
  extension="${fileName##*.}"
  if [[ $extension == "zip" ]]; then
    true
  else
    false
  fi
}

isNoExtension() {
  fileName="$(basename "$1")"
  extension="${fileName##*.}"
  if [[ $fileName == $extension ]]; then
    true
  else
    false
  fi
}

shouldExtract() {
  fileName="$(basename "$1")"
  extension="${fileName##*.}"

  if [[ -n $ignoreContains ]]; then
    if [[ $fileName == *"$ignoreContains"* ]]; then
      false
      return
    fi
  fi

  if [[ -n $extractContains ]]; then
    if [[ $fileName == *"$extractContains"* ]]; then
      true
      return
    else
      false
      return
    fi
  fi

  true
}

# 传参：
# $1 当前目录
# $2 提取目录
extractImageRecursively() {
  currentDir="$1"
  if [[ -z $currentDir ]]; then
    echo "需要传递当前目录"
    exit 3
  fi

  extractDir="$2"
  if [[ -z $extractDir ]]; then
    echo "需要传递提取目录"
    exit 4
  fi

  if [[ -d $currentDir ]]; then
    cd "$currentDir"

    needRecursiveExtractDirs=()
    for image in *; do
      imagePath="$currentDir""/"$image
      if [[ -f $imagePath ]]; then
        fileName="$(basename "$imagePath")"
        if shouldExtract "$imagePath"; then
          if isImage "$imagePath"; then
            newPath="$extractDir""/""$fileName"
            mv_no_override "$imagePath" "$newPath"
          elif isNoExtension "$imagePath"; then
            newPath="$extractDir""/""$fileName"".jpg"
            mv_no_override "$imagePath" "$newPath"
          fi
        fi
      elif [[ -d $imagePath ]]; then
        if [[ $imagePath == *$filterFolderContains* ]]; then
            echo "需要过滤当前包含特定字符的子文件夹"
        else
            needRecursiveExtractDirs+=("$imagePath")
        fi
      fi
    done

    # 递归的提取
    for dir in "${needRecursiveExtractDirs[@]}"; do
      extractImageRecursively "$dir" "$extractDir"
    done
  fi
}

mv_no_override() {
    local dir file ext base num
    if [ -d "$2" ]; then
        dir=$2
        file=$(basename "$1")
    else
        dir=$(dirname "$2")
        file=$(basename "$2")
    fi
    ext="$(sed -r 's/.+(\..+)|.*/\1/' <<<"$file")"
    base="$(sed -r 's/(.+)\..+|(.*)/\1\2/' <<<"$file")"
    while [ -e "$dir/$base$num$ext" ]; do
        (( num++ ))
    done
    mv "$1" "$dir/$base$num$ext"
}

#################
# 开始
#################

cd "$extractDir"

# 开始解压所有zip包
for file in *; do
  filePath="$extractDir""/""$file"
  if isZip "$filePath"; then
    fileName="$(basename "$filePath")"
    fileNameWithoutExtension="${fileName%.*}"
    unzip -o "$filePath" -d "$fileNameWithoutExtension"
  fi
done

# 开始提取所有图片
for file in *; do
  filePath="$extractDir""/""$file"
  extractImageRecursively "$filePath" "$extractDir"
done

# 删除目录和非图片文件
echo "$extractDir"
cd "$extractDir"
for file in *; do
  filePath="$extractDir""/""$file"
  if [[ -d $filePath ]]; then
    rm -rf "$filePath"
  else
    if ! isImage "$filePath"; then
      rm -rf "$filePath"
    fi
  fi
done

echo "完成提取目录：$extractDir"
echo "============================="
