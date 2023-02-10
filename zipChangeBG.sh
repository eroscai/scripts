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
echo "开始打包目录："$extractDir""

previewDir="封面"

makeDir() {
  currentDir="$1"
  if [[ -z $currentDir ]]; then
    echo "需要传递当前目录"
    exit 3
  fi

  extractDir="$2"
  if [[ -z $extractDir ]]; then
    echo "需要传递输出目录"
    exit 4
  fi

  if [[ -d $currentDir ]]; then
    cd "$currentDir"

    i=0
    for file in *; do
      filePath="$currentDir""/""$file"
      ext="$(sed -r 's/.+(\..+)|.*/\1/' <<<"$file")"
      if [[ -f "$filePath" ]]; then
        previewFilePath="$currentDir""/""$previewDir""/""$file"
        if [[ -f $previewFilePath ]]; then
          newDir="$currentDir""/zip/""$i"
          mkdir -p "$newDir"

          newFilePath="$newDir""/original$ext"
          newPreviewFilePath="$newDir""/normal$ext"
          mv_no_override "$filePath" "$newFilePath"
          mv_no_override "$previewFilePath" "$newPreviewFilePath"
          ((i=i+1))
        fi
      fi
    done
  fi
}

# 传参：
# $1 当前目录
# $2 提取目录
zipChangeBG() {
  currentDir="$1"
  if [[ -z $currentDir ]]; then
    echo "需要传递当前目录"
    exit 3
  fi

  extractDir="$2"
  if [[ -z $extractDir ]]; then
    echo "需要传递打包目录"
    exit 4
  fi

  if [[ -d $currentDir ]]; then
    cd "$currentDir"
    echo "$currentDir"

    zipPath="zip"
    if [[ -d $zipPath ]]; then
      echo "$zipPath"
      cd "$zipPath"
      fileName="$(basename "$currentDir")"
      fileNameWithExtension="$fileName.zip"
      zip -r "$fileNameWithExtension" "."

      newPath="$currentDir""/""$fileNameWithExtension"
      mv_no_override "$fileName.zip" "$newPath"
      cd ".."
    fi
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
# 先提取目录
for file in *; do
  filePath="$extractDir""/""$file"
  makeDir "$filePath" "$extractDir"
done

# 重新进入主目录
cd "$extractDir"
# 再开始打包
for file in *; do
  filePath="$extractDir""/""$file"
  zipChangeBG "$filePath" "$extractDir"
done

# 删除无用的zip文件夹
echo "$extractDir"
cd "$extractDir"
for directory in *; do
  directoryPath="$extractDir""/""$directory"

  if [[ -d $directoryPath ]]; then
    cd "$directoryPath"

    for file in *; do
      filePath="$directoryPath""/""$file"
      if [[ -d $filePath ]]; then
        if [[ $file == "zip" ]] || [[ $file == "$previewDir" ]]; then
          rm -rf "$filePath"
        fi
      fi
    done
  fi
done

echo "完成提取目录：$extractDir"
echo "============================="
