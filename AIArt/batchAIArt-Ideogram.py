import os
import json
import pandas as pd
import requests

# 定义有效比例列表
valid_ratios = [
    1.0 / 1.0,
    2.0 / 3.0,
    3.0 / 4.0,
    9.0 / 16.0
]

# 修剪宽度和高度的函数
def trim_size(width, height):
    # if width and height:
    #     ratio = width / height
    #     matched_index = 0
    #     ratio_gap = 100
    #     for i, valid_ratio in enumerate(valid_ratios):
    #         current_gap = abs(ratio - valid_ratio)
    #         if ratio_gap > current_gap:
    #             matched_index = i
    #             ratio_gap = current_gap

    #     valid_ratio = valid_ratios[matched_index]
    #     if valid_ratio >= 1:
    #         height = int((1024 / valid_ratio) / 8) * 8
    #         return 1024, height
    #     else:
    #         width = int((1024 * valid_ratio) / 8) * 8
    #         return width, 1024

    return width, height

def read_json_files(directory, download_directory, cover_ids):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    json_files.sort()  # 按照字母数字排序

    data_v1 = []
    data_v2 = []
    file_index = 1

    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            results = json_data.get('results', [])
            for result in results:
                prompt = ''
                for response in result.get('responses', []):
                    if response.get('cover', False):
                        prompt = response["prompt"]

                width, height = trim_size(result.get('width', 0), result.get('height', 0))

                cover_id = result.get('cover_response_id', '')
                model_version = result.get('model_version', '')
                is_v2 = model_version == 'V_1_5'
                cover_url = 'https://ideogram.ai/assets/progressive-image/balanced/response/' + cover_id
                filename = f'{file_index}.jpg'
                if is_v2:
                    target_url = download_directory + '/v2/' + filename
                else:
                    target_url = download_directory + '/v1/' + filename

                success = download_image(cover_url, target_url)
                # success = True
                if success:
                    if cover_id not in cover_ids:
                        data = {
                            "prompt": prompt,
                            'model_version': model_version,
                            "aspect_ratio": result.get('aspect_ratio', ''),
                            "cover_response_id": cover_id,
                            'width': width,
                            'height': height,
                            'filename': filename
                        }
                        if is_v2 :
                            data_v2.append(data)
                        else:
                            data_v1.append(data)
                    file_index += 1

    return (data_v1, data_v2)

# 下载图片函数
def download_image(url, save_path):
    # 已存在
    if os.path.exists(save_path):
        print(f"已存在： {save_path}")
        return True

    # 获取保存路径的目录部分
    directory = os.path.dirname(save_path)

    # 如果目录不存在，则创建
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"目录 {directory} 不存在，已创建。")

    print(f"开始下载: {url}")
    # 设置请求头，模拟浏览器
    headers = {
        'Cookie': '__cf_bm=rXHmkIBqMYrQ4Jx6o25lyMwmf4BiFoByen9WMotaKtw-1725897411-1.0.1.1-U8lIZ8Vl5Tfk4vTO4XxX5WZGSJ2oVaqJGo81dlYPeK0ifYr8xjPmHUFJlA2BJ9BFJOu90d7McfnTiEjLoCMr5A; _ga_44J8R31CP6=GS1.1.1725894895.1.1.1725894906.0.0.0; AMP_da0464495c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI2M2I3YmQ4Zi1kY2RjLTQ0YWQtYjExYS1kMWFkNjNmNjUwMzUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzI1ODk0ODk1NjI1JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTcyNTg5NDkwMTQwNiUyQyUyMmxhc3RFdmVudElkJTIyJTNBOCUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMiU3RA==; _ga=GA1.1.1478484158.1725894896; cf_clearance=xL3nwk3cL.tAVkmvcVGQeV7z5hhpka9xLJIgfPEv3UU-1725894896-1.2.1.1-Z3oVctYcUwm.KtkeZaqGOPepqH_Lg1_.JY9BKM2Tl7nnIPKobs_wmygHTxJtviwXG4ZFaEDVxbkpsLW7pNv8oVsisNS2Twb3D4kTaSnNoifZFzPu3.w8ISPn_9MIY1vlmlTtwZ68Z.Ci8SW8j8LbIOpAjuDZJJVe_wMu_5t3IXRXmpZL5.LDArIPCUBlWaDgOLuSxLjKoqX5X.MZys_mFzT_7ivefEIUnU4rJ6j5TIVXN.DCUNiftDb7mLWfe9QILLcj2LkqMUi88KHTGAKnfn9obfXVXFj3Yyd5xHa7dNWZRLcznTHprAEeH6jxBPwh6ShvypppS_5FN2XxQBmcFWsdfVo5D7LLzeu2djOcxBQugD30sujyR4HZS0L52bPmSj7jdk6jErM4GK9AY1HeLA; AMP_MKTG_da0464495c=JTdCJTdE',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    }
    # 发送GET请求
    response = requests.get(url, headers=headers)    

    print(f"结果: {response}")
    # 检查请求是否成功
    if response.status_code == 200:
        # 保存图片到指定路径
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"图片成功下载到: {save_path}")
        return True
    else:
        print(f"下载失败，状态码: {response.status_code}")
        return False

def extract_fields(file_path, sheet_name, field_name):
    # 使用 pandas 读取 Excel 文件
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    
    # 检查是否存在 'cover_response_id' 列
    if field_name in df.columns:
        # 提取 'cover_response_id' 列，去除 NaN 值并将其转换为列表
        filed_values = df[field_name].dropna().tolist()
        return filed_values
    else:
        print(f"没有找到 {field_name} 列")
        return []
    
# 定义一个函数来遍历目录并删除不需要的文件
def clean_directory(directory_path):
    response_file = directory_path + 'output.xlsx'
    download_file_path = directory_path + 'Download'
    filenames = extract_fields(response_file, 'Sheet1', 'filename')

    # 遍历目录中的所有文件
    for file_name in os.listdir(download_file_path):
        # 获取完整的文件路径
        file_path = os.path.join(download_file_path, file_name)

        # 检查是否为文件（忽略子目录）
        if os.path.isfile(file_path):
            # 判断文件名是否在给定的数组中
            if file_name not in filenames:
                # 如果不在数组中，删除文件
                try:
                    os.remove(file_path)
                    print(f"文件 {file_name} 已被删除")
                except Exception as e:
                    print(f"删除文件 {file_name} 时出错: {e}")
            else:
                print(f"文件 {file_name} 保留")
        else:
            print(f"跳过 {file_name}，因为它不是文件")

# 定义一个函数，将 Excel 转换为 JSON
def excel_to_json(excel_file_path, sheet_name, json_file_path):
    # 使用 pandas 读取 Excel 文件中的指定工作表
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, engine='openpyxl')

    # 将 DataFrame 转换为 JSON 格式
    json_data = df.to_json(orient='records', force_ascii=False)

    # 将 JSON 数据保存到文件
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print(f"Excel 文件已成功转换为 JSON 文件: {json_file_path}")

def save_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False, engine='openpyxl')

def main(directory, download_directory, cover_ids):
    (data_v1, data_v2) = read_json_files(directory, download_directory, cover_ids)

    output_file1 = directory + '/output_v1.xlsx'
    save_to_excel(data_v1, output_file1)
    output_file2 = directory + '/output_v2.xlsx'
    save_to_excel(data_v2, output_file2)

    print(f'Data has been successfully saved to {output_file1} {output_file2}')

if __name__ == '__main__':
    main_directory = '/Users/Eros/Downloads/Ideogram-week/'
    directory = main_directory + 'realistic/'  # 替换为你的JSON文件所在目录
    download_directory = directory + '/Download'

    output_files = main_directory + 'outputs'
    excel_files = [f for f in os.listdir(output_files) if f.endswith('.xlsx')]
    cover_ids = []
    for excel_file in excel_files:
        excel_file_path = output_files + '/' + excel_file
        ids = extract_fields(excel_file_path, 'Sheet1', 'cover_response_id')
        cover_ids.append(ids)

    main(directory, download_directory, cover_ids)

    # clean_directory(directory)

    # json_file = directory + '/output.json'
    # excel_to_json(output_file, "Sheet1", json_file)
