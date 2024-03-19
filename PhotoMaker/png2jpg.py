import os
from PIL import Image

def convert_png_to_jpg(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):
                # 构建完整的文件路径
                file_path = os.path.join(root, file)
                # 打开PNG图像
                img = Image.open(file_path)
                # 转换为RGB格式（JPG不支持透明度）
                rgb_img = img.convert('RGB')
                # 构建新的文件名和路径
                jpg_file_path = os.path.splitext(file_path)[0] + ".jpg"
                # 保存为JPG格式
                rgb_img.save(jpg_file_path)
                # 如果你想删除原始的PNG文件，可以取消下一行的注释
                os.remove(file_path)
                print(f"Converted and saved: {jpg_file_path}")

# 指定你想遍历的根目录
root_directory = '/Users/Eros/Downloads/Outputs'
convert_png_to_jpg(root_directory)
