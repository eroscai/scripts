import os
import requests
from PIL import Image
import io
import time

def compress_image(image_path, max_dimension=2048, max_file_size=2*1024*1024):
    """
    如果图片的宽度或高度超过1024像素，则缩放图片至最大边为1024像素。
    同时确保文件大小在2MB以下。

    :param image_path: 原始图片路径
    :param max_dimension: 最大宽度或高度
    :param max_file_size: 最大文件大小（字节）
    :return: 压缩后的图片对象
    """
    # 打开原始图片
    img = Image.open(image_path)
    original_size = os.path.getsize(image_path)

    # 检查图片的尺寸是否需要调整
    if img.size[0] > max_dimension or img.size[1] > max_dimension:
        # 计算新的尺寸，保持宽高比
        if img.size[0] > img.size[1]:
            new_height = int(max_dimension * (img.size[1] / img.size[0]))
            new_size = (max_dimension, new_height)
        else:
            new_width = int(max_dimension * (img.size[0] / img.size[1]))
            new_size = (new_width, max_dimension)
        
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # 将图片保存到一个字节流中，以便检查大小并在必要时调整质量
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes_size = img_bytes.tell()

    # 如果图片大小仍然超过限制，则尝试降低质量
    if img_bytes_size > max_file_size:
        for quality in range(100, 0, -5):
            img_bytes.seek(0)
            img_bytes.truncate()
            img.save(img_bytes, format='JPEG', quality=quality)
            if img_bytes.tell() <= max_file_size:
                break

    img_bytes.seek(0)
    return Image.open(img_bytes)

def download_file(url, directory, path):
    """
    下载文件到指定目录。

    :param url: 文件的 URL
    :param directory: 目标目录
    """
    if not os.path.exists(directory):
        os.makedirs(directory)  # 如果目录不存在，则创建目录
    
    local_filename = path.split('/')[-1]
    path = os.path.join(directory, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def check_task_status(task_id, url):
    """
    轮询任务状态。

    :param task_id: 任务ID
    :param url: 查询任务状态的 URL
    :return: 成功时的URL或None
    """
    timeout = 30
    start_time = time.time()
    headers = {'Authorization': f'Bearer {auth_token}'}
    while time.time() - start_time < timeout:
        response = requests.post(url, json={'taskid': task_id}, headers=headers)
        data = response.json().get('data', {})
        urls = data.get('url', [])
        if urls:  # 检查urls是否不为空
            return urls[0]  # 返回urls数组中的第一个URL
        time.sleep(3)  # 等待3秒再次查询
    return None

def post_image_and_process(image_path, upload_url, status_url, download_directory):
    """
    发起图片上传并处理任务。

    :param image_path: 图片路径
    :param upload_url: 图片上传的URL
    :param status_url: 查询任务状态的URL
    :param download_directory: 下载目录
    """
    img = compress_image(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    print(f'start {image_path}')
    files = {'sourceImage': ('image.jpg', img_byte_arr, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {auth_token}'}
    # data = {'destSize': destSize}
    # response = requests.post(upload_url, files=files, data=data, headers=headers)
    response = requests.post(upload_url, files=files, headers=headers)
    data = response.json().get('data', {})
    task_id = data.get('taskid')
    if task_id:
        print(f'check {image_path}')
        download_url = check_task_status(task_id, status_url)
        if download_url:
            download_file(download_url, download_directory, image_path)
            print(f"Downloaded {download_url} to {download_directory}")
        else:
            print(f"Task {task_id} timed out or failed.")
    else:
        print(f"Upload failed for {image_path}")


def recurse_and_process_images(directory, upload_url, status_url, download_directory):
    """
    递归处理目录中的所有图片。

    :param directory: 图片目录
    :param upload_url: 上传URL
    :param status_url: 状态查询URL
    :param download_directory: 下载目录
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(root, file)
                post_image_and_process(image_path, upload_url, status_url, download_directory)

# 使用示例
directory_path = 'xxx' # 修改为你的图片目录
upload_url = 'xxx' # 修改为你的接收图片的服务器地址
status_url = 'xxx' # 修改为查询任务状态的服务器地址
download_directory = 'xxx' # 修改为你的下载目录
auth_token = "xxx" # 修改为有效token
# destSize = 4 # 可选2或4，代表倍数

recurse_and_process_images(directory_path, upload_url, status_url, download_directory)
