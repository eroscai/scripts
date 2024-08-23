import os
import json
import pandas as pd
import math

# 定义有效比例列表
valid_ratios = [
    1.0 / 1.0,
    2.0 / 3.0,
    3.0 / 4.0,
    9.0 / 16.0
]

# 修剪宽度和高度的函数
def trim_size(width, height):
    if width and height:
        ratio = width / height
        matched_index = 0
        ratio_gap = 100
        for i, valid_ratio in enumerate(valid_ratios):
            current_gap = abs(ratio - valid_ratio)
            if ratio_gap > current_gap:
                matched_index = i
                ratio_gap = current_gap

        valid_ratio = valid_ratios[matched_index]
        if valid_ratio >= 1:
            height = int((1024 / valid_ratio) / 8) * 8
            return 1024, height
        else:
            width = int((1024 * valid_ratio) / 8) * 8
            return width, 1024

    return width, height

def read_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    json_files.sort()  # 按照字母数字排序

    data = []
    file_index = 301

    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            prompts = json_data.get('prompts', [])
            for prompt in prompts:
                cleaned_prompt = prompt.get('cleanedPrompt', '') or prompt.get('prompt', '')
                width, height = trim_size(prompt.get('width', 0), prompt.get('height', 0))
                data.append({
                    'id': prompt.get('id', ''),
                    'prompt': cleaned_prompt,
                    'negativePrompt': prompt.get('negativePrompt', ''),
                    'seed': prompt.get('seed', ''),
                    'width': width,
                    'height': height,
                    'step': 30,
                    'cfg': 6,
                    'filename': f'{file_index}.jpg'
                })
                file_index += 1

    return data

def save_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False, engine='openpyxl')

def main(directory, output_file):
    data = read_json_files(directory)
    save_to_excel(data, output_file)
    print(f'Data has been successfully saved to {output_file}')

if __name__ == '__main__':
    directory = '/Users/Eros/Downloads/Lexica/2P'  # 替换为你的JSON文件所在目录
    output_file = directory + '/output.xlsx'
    main(directory, output_file)