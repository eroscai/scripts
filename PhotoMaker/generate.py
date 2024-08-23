import itertools
import json
import requests
import json
import time
import tarfile
import os
from datetime import datetime, timedelta

def download_and_extract_tar_gz(url, extract_to):
    # 下载文件
    r = requests.get(url, verify=False)
    if r.status_code == 200:
        tar_gz_path = os.path.join(extract_to, 'downloaded_file.tar.gz')
        # 确保包含下载文件的目录存在
        os.makedirs(os.path.dirname(tar_gz_path), exist_ok=True)
        with open(tar_gz_path, 'wb') as f:
            f.write(r.content)
        print('File downloaded successfully:', tar_gz_path)

        # 解压缩tar.gz文件
        with tarfile.open(tar_gz_path, 'r:gz') as tar:
            tar.extractall(path=extract_to)
        print('File extracted successfully to:', extract_to)

        # 可选：删除下载的tar.gz文件
        os.remove(tar_gz_path)
        print('Downloaded tar.gz file removed.')
    else:
        print('Failed to download file:', r.status_code)

def send_post_request_and_poll(task_data, initial_url, poll_url, extract_to):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(initial_url, json=task_data, headers=headers, verify=False)
    print(response.json())
    if response.status_code == 200:
        task_ids = response.json().get('data', [])
        for task_id in task_ids:
            timeout = datetime.now() + timedelta(minutes=5)
            while datetime.now() < timeout:
                poll_data = {'task_id': task_id}
                poll_response = requests.post(poll_url, json=poll_data, headers=headers, verify=False)
                if poll_response.status_code == 200:
                    poll_response_json = poll_response.json()
                    # 检查响应体中的code字段是否为200
                    if poll_response_json.get("code") == 200:
                        file_urls = poll_response_json.get("data", [])
                        for file_url in file_urls:
                            print("Downloading and extracting file for task ID:", task_id)
                            final_extract_to = extract_to + "/" + task_data["output_folder"]
                            download_and_extract_tar_gz(file_url, final_extract_to)
                            return  # 假设每个任务只需要下载和解压第一个文件
                        break
                    else:
                        print("Polling failed with response code:", poll_response_json.get("code"))
                else:
                    print("Polling HTTP request failed:", poll_response.status_code)
                time.sleep(10)
            if datetime.now() >= timeout:
                print('Polling timed out after 5 minutes for task ID:', task_id)
    else:
        print('Failed to send initial POST request:', response.status_code, response.text)

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

def generate_tasks(person_images_file_path, prompts_file_path):
    person_images_arrays = read_json_file(person_images_file_path)
    prompts = read_json_file(prompts_file_path)
    tasks = []

    for images_array in person_images_arrays:
        j = 0
        for prompt in prompts:
            task = {
                "person_images": images_array,
                "prompt": prompt,
                "negative_prompt": "multiple person, long face, crooked face, drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly, anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, multiple face",
                "num_steps": 50,
                "style_strength_ratio": 20,
                "guidance_scale": 5.0,
                "output_width": 1024,
                "output_height": 1536,
                "num_images": 3,
                "output_folder": images_array[0] + "_" + str(j)
            }
            tasks.append(task)
            j += 1
    
    return tasks

def process_combined_tasks(tasks, initial_url, poll_url, extract_to):
    for task_data in tasks:
        # # 将任务数据转换为JSON字符串，确保使用双引号
        # task_data_json = json.dumps(task_data)
        # 假设send_post_request_and_poll函数接受JSON字符串作为参数
        print("Start Processing")
        send_post_request_and_poll(task_data, initial_url, poll_url, extract_to)
        print("Completed processing for one combined task. Moving to the next.")

# 示例文件路径
images_file_path = ''
prompts_file_path = ''
initial_url = ''
poll_url = ''
extract_to = ''

# 生成任务并处理
tasks = generate_tasks(images_file_path, prompts_file_path)
process_combined_tasks(tasks, initial_url, poll_url, extract_to)