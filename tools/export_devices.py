import click
import configparser
import requests
import os
import csv
import json
import time
import datetime
import qrcode
from urllib.parse import urlencode
from tqdm import tqdm
import pandas as pd
from lib.api_common import base_url, get_access_token
from lib.logger import log_info

devices = []
current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

@click.command('export_devices')
@click.option('--type_id', required=False, help='Device ID to export attributes history')
@click.option('--group_id', required=False, help='Device ID to export attributes history')
@click.option('--include_sub_groups', is_flag=True, required=False, default=False, help='包含子组的设备')
@click.option('--qrcode', is_flag=True, required=False, default=False, help='生成设备二维码')


def export_devices(type_id, group_id, include_sub_groups, qrcode):
    global devices
    access_token = get_access_token()
    if access_token == None:
        click.echo("API 身份验证失败，终止程序")
        return
    
    click.echo("API 身份验证成功")
    click.echo(f"开始导出数据到 {export_csv_path()}")
    data_header = ['设备ID', '设备名称', '设备类型', 'Device Key', '设备码']
    append_to_csv(data_header)
    
    get_devices(access_token, 1, type_id, group_id, include_sub_groups)
    click.echo(f"共找到 {len(devices)} 个设备")
    
    # 导出
    with tqdm(total=len(devices), desc="导出进度", unit="设备") as pbar:
        for device in devices:
            data = [device['id'], device['name'], device['type_name'], device['device_key'], device['device_code']]
            append_to_csv(data)
            time.sleep(0.1)
            if qrcode:
                file_name = f"{device['name']}{device['device_key']}"
                gen_qrcode(file_name, device['device_code'])
            pbar.update(1)
    
def get_devices(access_token, page, type_id, group_id, include_sub_groups):
    global devices
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    query = {
        'page_records': 50,
        'page': page,
    }
    if type_id:
        query['type'] = type_id
        click.echo(f"正在导出设备类型[{type_id}]下所有设备的属性历史数据")
    elif group_id:
        query['groups'] = group_id
        if include_sub_groups:
            query['include_sub_groups'] = '1'
        click.echo(f"正在导出设备组[{group_id}]下所有设备的属性历史数据")

    api_url = base_url() + "/api/v1/devices?" + urlencode(query)
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        log_info(data)
        if data['result']:
            for device in data['info']['items']:
                click.echo(f"找到设备 [{device['id']} - {device['name']}]")
                type_info = device.get('type_info', {})
                devices.append({
                    'id': device['id'],
                    'name': device['name'],
                    'type_name': type_info.get('name', ''),
                    'device_key': device.get('device_key', ''),
                    'device_code': device.get('device_code', ''),
                })
            page_total = data['info']['page_total']
            if page_total > page:
                time.sleep(1)
                get_devices(access_token, page+1, type_id, group_id, include_sub_groups)
                    
        else:
            print(f"请求失败！返回结果: {response.json()}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")


def gen_qrcode(file_name, device_code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = {
        'device_code': device_code,
    }
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_path = f"{export_qrcode_path()}/qrcode_{file_name}.png"
    img.save(img_path)
    click.echo(f"设备二维码已生成 -> {img_path}")

def export_qrcode_path():
    path = f'export/{current_time}'
    if not os.path.exists(path):
        os.makedirs(path)
    return path
    
def export_csv_path():
    return f'export/{current_time}.csv'
    
def append_to_csv(data):
    with open(export_csv_path(), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
