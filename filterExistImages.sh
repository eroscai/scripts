#!/bin/bash
# exit when any command fails
set -e

usage() { echo "$0 usage:" && grep " .)\ #" $0; exit 0; }
[ $# -eq 0 ] && usage

while getopts ":d:e" opt; do
  case $opt in
    d) # 当前要执行的完整目录地址
      extractDir="$OPTARG"
      ;;
    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done

echo $extractDir
if [ -z "$extractDir" ]; then
  echo "执行脚本时请带上目录路径"
  exit 2
fi

echo "============================="
echo "开始筛选目录："$extractDir""

isImage() {
  fileName="$(basename "$1")"
  extension="${fileName##*.}"
  if [[ $extension == "jpg" ]] || [[ $extension == "png" ]]; then
    true
  else
    false
  fi
}

# 传参：
# $1 参考目录
# $2 原始目录
filterExistImages() {
  originalPath="$1"
  if [[ -z $originalPath ]]; then
    echo "需要传递原始文件目录"
    exit 3
  fi

  gtPath="$2"
  if [[ -z $gtPath ]]; then
    echo "需要传递待筛选目录"
    exit 4
  fi

  extractDir="$3"
  if [[ -z $extractDir ]]; then
    echo "需要传递提取目录"
    exit 5
  fi

  originalFileNames=()
  cd $originalPath
  for file in *; do
      if isImage "$file"; then
          originalFileNames+=("$file")
      fi
  done

  cd ".."
  extractPath=$extractDir"extract-gt/"
  if [[ ! -d $extractPath ]]; then
    mkdir $extractPath
  fi

  if [[ -d $gtPath ]]; then
    cd "$gtPath"

    for file in "${originalFileNames[@]}"; do
      filePath="$gtPath""/""$file"
      if [[ -f "$file" ]]; then
        newPath="$extractPath""$file"
        echo "$filePath"
        echo "$newPath"
        mv_no_override "$filePath" "$newPath"
      fi
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

gtPath="$extractDir""/gt"
originalPath="$extractDir""/original"

# 开始筛选
filterExistImages "$originalPath" "$gtPath" "$extractDir"

echo "完成筛选目录：$extractDir"
echo "============================="