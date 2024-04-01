import os
import requests
from PIL import Image
import io
import time
import random
import sys

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
            return urls
        print(f"{data}")
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
    img = Image.open(image_path)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    directory = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)

    styles = [
        "Create an image of a stylish individual in a winter setting. The person has long, wavy hair and is wearing reflective ski goggles on their head. They are dressed in winter attire suitable for skiing, including a white jacket with a fur-lined hood, and a high-necked layer underneath. The background is a picturesque snowy landscape with pine trees and a cozy wooden chalet. The sky is clear and blue, indicating a crisp, sunny day. The individual is centered in the frame, looking into the camera with a relaxed yet poised expression",
        "Create an image of a person outfitted for a winter adventure. They have a fashionable winter look, featuring oversized sunglasses and a trendy beanie with a noticeable logo. The beanie is white with a patterned design. They are wearing a glossy, metallic puffer jacket that reflects the light, giving a cool, silvery sheen. The background is a mountainous, snowy landscape with overcast skies, suggesting a cold winter day. Despite the chilly environment, the person's posture is confident, and their expression is poised, with a touch of sophistication",
        "Generate an image of a happy person riding in a ski lift, dressed for skiing. The individual has a sporty look with a bright yellow and black ski jacket and is wearing large ski goggles with reflective multicolored lenses that cover the eyes. Their hair is casually styled, and they have a joyful smile. The environment inside the lift is cozy, contrasting with the snowy mountainous scenery visible through the windows. The picture captures a sense of height and exhilaration, evoking the excitement of skiing down the slopes",
        "Visualize a dedicated athlete engaged in an intense workout inside a well-equipped gym. The individual is muscular and wearing a tight-fitting, short-sleeved gray athletic shirt that accentuates their physique, paired with dark workout shorts. They are seated, performing bicep curls with a heavy dumbbell, displaying prominent arm muscles and focus in their expression. The gym has a modern look with various pieces of equipment in the background, slightly blurred to keep the focus on the person. The lighting is dynamic, with high contrast, creating deep shadows that further define the muscles and contours of the individual's body",
        "A muscular shirtless man with dark hair and a beard, sporting intricate tattoos on his arm and chest, wearing faded blue jeans, standing against a plain grey studio background, dramatic lighting accentuating his toned physique and tattoos, highly detailed facial features and muscles, photorealistic style, 8K resolution",
        "A close-up portrait of a young man with curly brown hair and a beard, shirtless with water droplets on his skin, immersed in a blue-tiled swimming pool at night with trees in the background, realistic lighting and reflections in the water, highly detailed facial features and textures, cinematic shot, 8K resolution",
        "Create a black and white full-length portrait of a person with strong, prominent features, including the waist. The facial features are clear, high-definition, and clear, with many details. The photo is black and white. The person has a relaxed and delicate hairstyle with a natural and elegant style. No hands, obvious facial features, expressive expression, exuding confidence, very confident and charming, wearing a simple tight-fitting long-sleeved turtleneck bottoming shirt, pure white or pure black tight-fitting, simple and versatile style, which gives The image adds bold yet casual elegance. The lighting is soft, creating an effect of light and shadow that accentuates the texture of the hair, the depth of the eyes, and the contours of the face. A simple solid color background with a simple background ensures that the person's face is the focus of the portrait, shot in a studio.",
        "A male model wears black jeans and an elegant black turtleneck sweater, standing with his arms hanging naturally at his sides. Clear facial features, gray background, photo taken on Hasselblad film in the style of Peter Lindbergh. He has dark hair and light skin and exudes confidence as he poses for the camera. His gaze draws attention while also adding to the overall elegance of the portrait. This photo showcases the fine details of texture and fabric quality, creating a timeless look that adds depth to your visual narrative. Real photos, with strong sense of realism, highly detailed facial features and shooting lenses, 8K resolution",
    ]

    sizes = [
        [1024, 1024],
        [1280, 768],
        [768, 1280]
    ]

    i = 0
    for style in styles:
        i += 1
        for size in sizes:    
            print(f'start {image_path}')
            files = {'sourceImage': ('image.jpg', img_byte_arr, 'image/jpeg')}
            headers = {'Authorization': f'Bearer {auth_token}'}
            seed = random.randint(1, sys.maxsize - 1)  # 生成随机seed值
            data = {
                'positivePrompt': style,
                'imgWidth': size[0],
                'imgHeight': size[1],
                'seed': seed,
                'num': 1
            }
            response = requests.post(upload_url, files=files, data=data, headers=headers)
            data = response.json().get('data', {})
            task_id = data.get('taskid')
            if task_id:
                print(f'check {image_path}, task_id {task_id}')
                download_urls = check_task_status(task_id, status_url)
                if download_urls:
                    for download_url in download_urls:
                        download_path = os.path.join(directory, f"{file_name}_{size[0]}_{size[1]}_{i}.jpg")
                        download_file(download_url, download_directory, download_path)
                        print(f"Downloaded {download_url} to {download_path}")
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
