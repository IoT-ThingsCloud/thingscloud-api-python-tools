import click
import configparser
import requests
import csv
import json
import time
import datetime
from urllib.parse import urlencode
from tqdm import tqdm
import pandas as pd
from lib.api_common import base_url, get_access_token
from lib.logger import log_info

@click.command('create_devices')
@click.option('--file_path', default='import/create_devices_template.csv', required=False, show_default=True, help='指定导入的 CSV 文件路径')
@click.option('--type_id', required=True, help='为创建的设备指定设备类型 ID')

def create_devices(file_path, type_id):
    
    access_token = get_access_token()
    if access_token == None:
        click.echo("API 身份验证失败，终止程序")
        return
    
    click.echo("API 身份验证成功")
    click.echo(f"开始读取导入文件 {file_path}")
    
    # 读取 CSV 文件
    try:
        df = pd.read_csv(file_path)
        click.echo(f"共读取 {len(df)} 个设备")
        with tqdm(total=len(df), desc="创建进度", unit="设备") as pbar:
            for index, row in df.iterrows():
                name = str(row["name"])
                device_key = str(row["device_key"])
                # 判断 device_key 在这一行中是否存在
                if pd.isnull(row["device_key"]):
                    device_key = ""
                click.echo(f"开始导入设备[{name} - {device_key}]")
                create_device(access_token, name, device_key, type_id)
                time.sleep(1)
                pbar.update(1)
    except FileNotFoundError:
        print("找不到 CSV 文件")
    except Exception as e:
        print(f"打开文件发生异常: {str(e)}")
    
def create_device(access_token, name, device_key, type_id):
    
    payload = {
        "name": name,
        "type": type_id,
        "device_key": device_key,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    api_url = base_url() + "/api/v1/device"
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['result']:
            print(f"设备 [{name}] 创建成功！返回结果: {response.json()}")
        else:
            print(f"设备 [{name}] 创建失败！返回结果: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"设备 [{name}] 请求发生错误: {str(e)}")