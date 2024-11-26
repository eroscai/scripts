import os
import requests
from PIL import Image
import io
import time
import random
import sys

def download_file(url, directory, local_filename):
    """
    下载文件到指定目录。

    :param url: 文件的 URL
    :param directory: 目标目录
    """
    if not os.path.exists(directory):
        os.makedirs(directory)  # 如果目录不存在，则创建目录
    
    path = os.path.join(directory, local_filename)
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.RequestException as e:
        print(f"发生错误：{e}")

    return local_filename

def check_task_status(task_id, url):
    """
    轮询任务状态。

    :param task_id: 任务ID
    :param url: 查询任务状态的 URL
    :return: 成功时的URL或None
    """
    timeout = 300
    start_time = time.time()
    headers = {'Authorization': f'Bearer {auth_token}'}
    while time.time() - start_time < timeout:
        response = requests.post(url, json={'taskid': task_id}, headers=headers)
        data = response.json().get('data', {})
        urls = data.get('url', [])
        if urls:  # 检查urls是否不为空
            return urls
        status = data.get('image_status', 0)
        if status == 4:
            return None
        print(f"{data}")
        time.sleep(3)  # 等待3秒再次查询
    return None

def post_image_and_process(image_path, upload_url, status_url, download_directory, style_images):
    """
    发起图片上传并处理任务。

    :param image_path: 图片路径
    :param upload_url: 图片上传的URL
    :param status_url: 查询任务状态的URL
    :param download_directory: 下载目录
    """
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    directory = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)

    for pose_image_path in style_images:
        pose_img = Image.open(pose_image_path)
        pose_img_byte_arr = io.BytesIO()
        pose_img.save(pose_img_byte_arr, format='JPEG')
        pose_img_byte_arr = pose_img_byte_arr.getvalue()
        print(f'start {image_path} {pose_image_path}')
        files = {
            'sourceImage': ('sourceImage.jpg', img_byte_arr, 'image/jpeg'),
            'templateImage': ('poseImage.jpg', pose_img_byte_arr, 'image/jpeg')
        }
        headers = {'Authorization': f'Bearer {auth_token}'}
        seed = random.randint(1, sys.maxsize - 1)  # 生成随机seed值
        data = {}

        try:
            response = requests.post(upload_url, files=files, data=data, headers=headers)
            print(response.json())
            data = response.json().get('data', {})
            task_id = data.get('taskid')
            if task_id:
                print(f'check {image_path}, task_id {task_id}')
                download_urls = check_task_status(task_id, status_url)
                if download_urls:
                    j = 0
                    for download_url in download_urls:
                        j += 1
                        download_directory_path = download_directory
                        download_file_name = f"{file_name}_{seed}.jpg"
                        download_file(download_url, download_directory_path, download_file_name)
                        print(f"Downloaded {download_url} to {download_directory_path}")
                else:
                    print(f"Task {task_id} timed out or failed.")
            else:
                print(f"Upload failed for {image_path}")
        except requests.RequestException as e:
            print(f"发生错误：{e}")



def recurse_and_process_images(directory, upload_url, status_url, download_directory, pose_images):
    if len(pose_images) <= 0:
        print("姿势图片不能为空！")
        return

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
                post_image_and_process(image_path, upload_url, status_url, download_directory, pose_images)

def fetch_style_images(directory):
    pose_images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(root, file)
                pose_images.append(image_path)
    return pose_images

# 使用示例
directory_path = '/xxx/Origin' # 修改为你的图片目录
style_directory_path = '/xxx/Styles' # 修改为你的图片目录
upload_url = 'http://xxx/v1/stylersync/stylersync' # 修改为你的接收图片的服务器地址
status_url = 'http://xxx/v1/stylersync/infobytaskid' # 修改为查询任务状态的服务器地址
download_directory = '/xxx/Downloads' # 修改为你的下载目录
auth_token = "" # 修改为有效token
# destSize = 4 # 可选2或4，代表倍数

style_images = fetch_style_images(style_directory_path)
recurse_and_process_images(directory_path, upload_url, status_url, download_directory, style_images)