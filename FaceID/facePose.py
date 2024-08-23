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
        print(f"{data}")
        time.sleep(3)  # 等待3秒再次查询
    return None

def post_image_and_process(image_path, upload_url, status_url, download_directory, pose_images):
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

    styles = [
        "High-definition, (half body: 1.5), above the waist, American photography studio photos, black turtleneck tight bottoming shirt, elegant, elegant, artistic, super confident and elegant expression, dark background, gradient background, background glare, dark corners of the screen, glare , high contrast, contour light, studio shooting, blocked light and shadow effects, strong shadows, backlighting, back-to-light",
        "HD, (waist above: 1.5), (person centered: 1.5), standing, American photography studio photo, black turtleneck tight top, jeans, elegant, elegant, artistic, super confident elegant expression, gray background, gradient Background, strong background light, vignetting, strong light, high contrast, contour light, studio shooting, blocked light and shadow effects, strong shadows, backlighting",
        "High definition, (half body: 1.5), above the waist, black professional suit, white shirt, elegant, elegant, artistic, super confident and elegant expression smile, American dark gray tie-dyed mottled background paper, dark corners, strong light, high contrast, contour light, studio shooting , blocked light and shadow effects, strong shadows, backlighting, back-to-light",
        "HD, (half body: 1.5), (above waist: 1.5), (dark blue business suit: 1.5), suit, (white shirt: 1.5), elegant, elegant, artistic, super confident, elegant expression smile, (blurred American style Dark gray blurred mottled background paper: 1), (background blur: 0.5), vignetting, strong light, high contrast, contour light, studio shooting, blocked light and shadow effects, strong shadows, backlighting, back facing",
        "A person standing on an outdoor office roof in New York City, (half body: 1.5) (looking at camera: 1.5), (high saturation: 1.5), (hands in pockets: 1.5), (skyscrapers in background near glass wall: 1.5 ), bright sunshine, blue sky and white clouds, sunny, (wearing dark gray suit: 1.5), (white shirt: 1.2), using cameras Sony α9 II and Sony FE 100-400mm f/4. 5-5. 6 GM OSS lens, high contrast, high details, real, high saturation, bright colors, clear weather, good air quality, high visibility, ultra-high definition, many details, soft light, diffuse reflection, cinematic feel, workplace,",
        "A person walking on a modern and simple street, consistent with his age, a city street at night, the crowd on the street is focused, (cold tone of the picture: 1.5), (half-length shot: 1.2), direct positioning candid shot, frontal shot, background blur, deformation Lens flare, (wearing black suit: 1.5), hands in pockets, smiling, soulful and relaxed, dim lighting, post-rain environment, high detail, realistic, UHD, high detail, dark color, UHD, high detail, soft light, Cinematic, realistic, realistic style, 8K resolution,",
    ]

    # seeds = [
    #     3230133849045017490,
    #     2938140724913030665,
    #     8308845219164532816,
    #     1254183629332398295,
    #     1254494625968411477,
    #     1635293158611111683,
    #     421411319690495071,
    #     4434649611110291428,
    #     4187370821345107159,
    #     5674012018125544512,
    #     6404910287133541828,
    #     949066771735059730,
    #     2233950852209372780,
    #     2861497503573541977,
    #     8613744465976695141,
    #     6076864550955409893
    # ]
    seeds = [
        4782660380427197381
    ]

    sizes = [
        # [1024, 1024],
        # [1280, 768],
        [856, 1280]
    ]

    i = 0
    k = 0
    for pose_image_path in pose_images:
        pose_img = Image.open(pose_image_path)
        pose_img_byte_arr = io.BytesIO()
        pose_img.save(pose_img_byte_arr, format='JPEG')
        pose_img_byte_arr = pose_img_byte_arr.getvalue()
        k += 1
        for style in styles:
            i += 1
            for size in sizes:
                l = 1
                while l > 0:
                    l -= 1
                # for seed in seeds:
                    print(f'start {image_path}')
                    files = {
                        'sourceImage': ('sourceImage.jpg', img_byte_arr, 'image/jpeg'),
                        'poseImage': ('poseImage.jpg', pose_img_byte_arr, 'image/jpeg')
                    }
                    headers = {'Authorization': f'Bearer {auth_token}'}
                    seed = random.randint(1, sys.maxsize - 1)  # 生成随机seed值
                    data = {
                        'positivePrompt': style,
                        'img_width': size[0],
                        'img_height': size[1],
                        'seed': seed,
                        'num': 1
                    }
                    print(f"{data}")

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
                                    download_directory_path = os.path.join(download_directory, f"{k}")
                                    # download_directory_path = download_directory
                                    download_file_name = f"{file_name}_{seed}_w{size[0]}_h{size[1]}_{i}_{j}_{k}.jpg"
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

def fetch_pose_images(directory):
    pose_images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(root, file)
                pose_images.append(image_path)
    return pose_images

# 使用示例
directory_path = '' # 修改为你的图片目录
pose_directory_path = '' # 修改为你的图片目录
upload_url = '' # 修改为你的接收图片的服务器地址
status_url = '' # 修改为查询任务状态的服务器地址
download_directory = '' # 修改为你的下载目录
auth_token = "" # 修改为有效token
# destSize = 4 # 可选2或4，代表倍数

pose_images = fetch_pose_images(pose_directory_path)
recurse_and_process_images(directory_path, upload_url, status_url, download_directory, pose_images)