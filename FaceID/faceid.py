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
        # "The image features a beautiful young woman, a tan sweater, standing in front of a building, hair pulled back in a bun. The woman is smiling, giving off a warm and friendly vibe. The scene captures a casual and comfortable moment, with the woman dressed in a cozy and stylish outfit.",
        "(masterpiece:1.0) , (best quality:1.4) , (ultra highres:1.2) , (photorealistic:1.4) , (8k, RAW photo:1.2) , (soft focus:1.4) , posh, (sharp focus:1.4) , (korean:1.2) , (american:1.1) , detailed beautiful face, (detailed open blazer:1.4) , tie, beautiful white shiny humid skin",
        # "full body photo ((extremely attractive) ) woman, long curly ginger hair, perfect eyes, (freckles:0. 2, light makeup, black blouse, long dress clothes, sitting on the end of her bed in her bedroom, gorgeous smile, bright sunlight coming through the windows, sheer curtains diffusing the sunlight . large depth of field, deep depth of field, highly detailed, highly detailed, 8k sharp focus, ultra photorealism",
        # "HDR photo of beautiful young woman, from behind, looking over her shoulder, long bronze hair, light-blue eyes, fair complexion, (freckles:0.5) , light makeup, light colored lipstick, gorgeous off the shoulder blouse, standing in a very dark room, large windows in the background . High dynamic range, vivid, rich details, clear shadows and highlights, realistic, intense, enhanced contrast, highly detailed",
        # "A Full body Photo High Definition Photograph of a joyous woman, holding a cellphone, happy and smiling, long bronze hair in a ponytail, light-blue eyes, fair complexion, (freckles:0.5) , sports bra, spandex shorts, inside a gym, walking towards 3rd viewer, glimmering skin . High dynamic range, vivid, rich details, clear shadows and highlights, realistic, intense, enhanced contrast, highly detailed, 8k sharp focus, ultra photorealism beauty, (Professionally advertised inside of a gym)",
        # "breathtaking fit woman, Karina Doherty, big smile, long brunette hair with blonde highlights, hazel eyes, lightly tanned skin, wearing a tank top, braided hair, leaning next to a window at night . award-winning, professional, highly detailed",
        # "((best quality) ), ((masterpiece) ), closeup of a beautiful french 20 year old woman, wearing a red summer dress, standing in a neon light alley at night in tokyo, absurdres, HDR",
        # "Create a sophisticated headshot that captures the essence of a professional, poised for success. The individual is styled in a sleek black blazer, its fabric catching the light with a subtle sheen, contrasted by the crisp, pure white of a well-pressed shirt. This attire exudes an air of classic elegance. The subject's expression is one of warm professionalism, with a smile that speaks to both confidence and congeniality. The backdrop suggests a high-end corporate environment, with a blurred hint of tasteful decor and ambient lighting that casts a gentle glow on the subject, highlighting their best features. (Hands in trouser pockets: 2), (half body: 1.5)",
        # "Generate an intricate digital headshot where the focus is on a person adorned in a textured blazer that whispers quality and style. The fabric has a herringbone pattern that adds depth to the image, paired with a tie that features a discreet, refined motif. The individual's face is the picture of friendly assurance, with a slight tilt of the head that invites trust and conveys leadership. The background is an understated gradient, perhaps the hint of a prestigious office wall, ensuring that the subject remains the star of this visual narrative. The lighting is masterful, with a chiaroscuro effect that adds dimensionality to the face and a touch of sparkle in the eyes that suggests ambition tempered with empathy.",
        # "A half-length photo of a European city travel photo of a person standing on a mountaintop looking at the camera, natural night light, natural light source, behind the person is an overhead shot above the city, the person is wearing casual black clothes, the shooting angle of the person is similar to the city The shooting angle remains consistent, and the photo captures the position of the character's thigh. It has the most popular ins makeup in 2024 and the hairstyle is relatively delicate, creating a relaxed and refined atmosphere. The whole photo has a blue tone, with an ins style, a light hazy filter, an ins filter, and was taken casually with a mobile phone. There are beautiful clouds at the junction of the sky and the city. There are a lot of light pinks at the bottom of the sky. The sky is gradient. The contrast and saturation of the picture are low, and there are dry spots. The characters are clear, and the characters and the background are very harmonious. The person's posture is confident, his eyes are staring into the distance, and looking towards the camera. The light of the figures and the background are consistent, natural light, and the background features the silhouettes of buildings, suggesting the bustling cityscape as the day draws to a close. Taken with a mobile phone, the photos are very natural and very casual. The face is clear and the skin texture is clear,",
        # "Generate a selfie of a young man sitting in the front seat of a car during prime time. The arm is stretched relatively long, and the selfie can be taken from the waist up. The arm is stretched relatively long, the expression is calm and happy, exquisite ins makeup, the popular ins makeup in 2024, confident smile, very confident, and confident about my appearance Very satisfied, looking directly at the camera, face with natural light, wearing a white round-neck pure cotton short-sleeved T-shirt, white pure cotton short-sleeved T-shirt, the color must be white, the weather is very good, the sun is bright, the sun shines through the car window , casting the shadow of the window frame on the character and inside the car. The sun hits the body, highlighting the texture of her hair and the contours of her facial features. Highly detailed facial features and muscles, realistic style, 8K resolution, facial details, clear skin texture",
        # "Display beautiful and healthy muscles with clear facial features, face profile 45 degrees, intricate tattoos on arms and chest, faded blue jeans, smiling with a confident and generous expression, standing against a solid gray studio background, photo Photographed in the style of Peter Lindbergh on Hasselblad film. His gaze draws attention while also adding to the overall sense of personality in the portrait. This photo showcases the fine details of texture and fabric quality, creating a timeless look that adds depth to your visual narrative. Dramatic lighting highlights his toned physique and tattoos, highly detailed facial features and muscles, realistic style, 8K resolution",
        # "A muscular man with a good figure, upper body, clear facial features, 45-degree facial profile, many complex tattoos on his body, large areas of tattoos on his body, a very cool expression, wearing dark pants, standing on a plain gray Studio background, photograph shot on Hasselblad film in the style of Peter Lindbergh. His gaze draws attention while also adding to the overall sense of personality in the portrait. This photo showcases the fine details of texture and fabric quality, creating a timeless look that adds depth to your visual narrative. Dramatic lighting highlights his toned physique and tattoos, highly detailed facial features and muscles, realistic style, 8K resolution",
        # "Side view of a person looking at the camera, smiling happily, full body portrait, far scene, water droplets on the skin, immersed in a blue tiled swimming pool during the day, sunlight shining down, posture lying sideways by the pool, hair is wet, composition The characters in the picture occupy 10:3, and the background accounts for 10:7. The background is trees, a large scene, the scene is relatively large, long-distance shooting, realistic lights and reflections in the water, real photos, and a strong sense of reality. , highly detailed facial features and textures, cinematic footage, 8K resolution,",
        # "Create a black and white full-length portrait of a person with strong, prominent features, including the waist. The facial features are clear, high-definition, and clear, with many details. The photo is black and white. The person has a relaxed and delicate hairstyle with a natural and elegant style. No hands, obvious facial features, expressive expression, exuding confidence, very confident and charming, wearing a simple tight-fitting long-sleeved turtleneck bottoming shirt, pure white or pure black tight-fitting, simple and versatile style, which gives The image adds bold yet casual elegance. The lighting is soft, creating an effect of light and shadow that accentuates the texture of the hair, the depth of the eyes, and the contours of the face. A simple solid color background with a simple background ensures that the person's face is the focus of the portrait, shot in a studio.",
        # "A male model wears black jeans and an elegant black turtleneck sweater, standing with his arms hanging naturally at his sides. Clear facial features, gray background, photo taken on Hasselblad film in the style of Peter Lindbergh. He has dark hair and light skin and exudes confidence as he poses for the camera. His gaze draws attention while also adding to the overall elegance of the portrait. This photo showcases the fine details of texture and fabric quality, creating a timeless look that adds depth to your visual narrative. Real photos, with strong sense of realism, highly detailed facial features and shooting lenses, 8K resolution",
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
        [768, 1280]
    ]

    i = 0
    for style in styles:
        i += 1
        for size in sizes:    
            for seed in seeds:
                print(f'start {image_path}')
                files = {'sourceImage': ('image.jpg', img_byte_arr, 'image/jpeg')}
                headers = {'Authorization': f'Bearer {auth_token}'}
                # seed = random.randint(1, sys.maxsize - 1)  # 生成随机seed值
                data = {
                    'positivePrompt': style,
                    # 'negativePrompt': "(exposed breasts: 2)",
                    'img_width': size[0],
                    'img_height': size[1],
                    'seed': seed,
                    'num': 3
                }
                print(f"{data}")

                try:
                    response = requests.post(upload_url, files=files, data=data, headers=headers)
                    data = response.json().get('data', {})
                    task_id = data.get('taskid')
                    if task_id:
                        print(f'check {image_path}, task_id {task_id}')
                        download_urls = check_task_status(task_id, status_url)
                        if download_urls:
                            j = 0
                            for download_url in download_urls:
                                j += 1
                                # download_directory_path = os.path.join(download_directory, f"{seed}")
                                download_directory_path = download_directory
                                download_file_name = f"{file_name}_{seed}_w{size[0]}_h{size[1]}_{i}_{j}.jpg"
                                download_file(download_url, download_directory_path, download_file_name)
                                print(f"Downloaded {download_url} to {download_directory_path}")
                        else:
                            print(f"Task {task_id} timed out or failed.")
                    else:
                        print(f"Upload failed for {image_path}")
                except requests.RequestException as e:
                    print(f"发生错误：{e}")


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
