import click
import configparser
import requests
import csv
import json
import time
import datetime
from urllib.parse import urlencode
from tqdm import tqdm
from lib.api_common import base_url, get_access_token
from lib.logger import log_info

devices = []
current_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

@click.command('export_devices_certificates')
@click.option('--device_id', required=False, help='指定导出证书的设备 ID')
@click.option('--type_id', required=False, help='指定导出证书的设备类型 ID')
@click.option('--group_id', required=False, help='指定导出证书的设备组 ID，支持多个 ID 通过逗号分隔')
@click.option('--include_sub_groups', is_flag=True, required=False, default=False, help='是否包含子组的设备')

def export_devices_certificates(device_id, type_id, group_id, include_sub_groups):
    
    access_token = get_access_token()
    if access_token == None:
        click.echo("API 身份验证失败，终止程序")
        return
    
    click.echo("API 身份验证成功")
    click.echo(f"开始导出设备证书到 {export_csv_path()}")
    data_header = ['设备名称', '设备类型', '证书内容']
    append_to_csv(data_header)
    
    get_devices(access_token, 1, device_id, type_id, group_id, include_sub_groups)
    click.echo(f"共找到 {len(devices)} 个设备")
    
    total_devices = len(devices)
    with tqdm(total=total_devices, desc="总进度", unit="设备") as pbar:
        for device in devices:
            certificate = get_device_certificate(access_token, device['id'])
            time.sleep(1)
            if certificate:
                data = [device['name'], device['type_name'], certificate]
                append_to_csv(data)
            pbar.update(1)

def get_devices(access_token, page, device_id, type_id, group_id, include_sub_groups):
    global devices
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    if device_id:
        click.echo(f"正在导出设备 {device_id} 的证书")
        api_url = base_url() + "/api/v1/device/" + device_id
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['result']:
                device = data['info']
                log_info(f"设备 [{device['id']} - {device['name']}]")
                type_info = device.get('type_info', {})
                devices.append({
                    'id': device['id'],
                    'name': device['name'],
                    'type_name': type_info.get('name', ''),
                }) 
            else:
                print(f"请求失败！返回结果: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {str(e)}")
    else:
        query = {
            'page_records': 100,
            'page': page,
        }
        if type_id:
            query['type'] = type_id
            click.echo(f"正在导出设备类型[{type_id}]下所有设备的证书")
        elif group_id:
            query['groups'] = group_id
            if include_sub_groups:
                query['include_sub_groups'] = '1'
            click.echo(f"正在导出设备组[{group_id}]下所有设备的证书")

        api_url = base_url() + "/api/v1/devices?" + urlencode(query)
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['result']:
                for device in data['info']['items']:
                    click.echo(f"找到设备 [{device['id']} - {device['name']}]")
                    type_info = device.get('type_info', {})
                    devices.append({
                        'id': device['id'],
                        'name': device['name'],
                        'type_name': type_info.get('name', ''),
                    })
                page_total = data['info']['page_total']
                if page_total > page:
                    time.sleep(1)
                    get_devices(access_token, page+1, device_id, type_id, group_id, include_sub_groups)
                        
            else:
                print(f"请求失败！返回结果: {response.json()}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {str(e)}")

def get_device_certificate(access_token, device_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # 请根据官方文档替换为正确的 API 路径
    api_url = base_url() + "/api/v1/device/" + str(device_id) + "/certificate"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['result']:
            return data['info']['access_token']
        else:
            print(f"请求失败！返回结果: {response.json()}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")

def export_csv_path():
    return f'export/certificates_{current_time}.csv'
    
def append_to_csv(data):
    with open(export_csv_path(), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

if __name__ == '__main__':
    export_devices_certificates()
