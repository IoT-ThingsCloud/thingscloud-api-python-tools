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
series_page_records = 500

@click.command('export_devices_attributes_history')
@click.option('--path', default='export/example.csv', required=True, help='Path to save the exported devices')
@click.option('--device_id', required=False, help='Device ID to export attributes history')
@click.option('--device_type_id', required=False, help='Device ID to export attributes history')
@click.option('--device_group_id', required=False, help='Device ID to export attributes history')
@click.option('--include_sub_groups', is_flag=True, required=False, default=False, help='包含子组的设备')
@click.option('--start_time', required=False, help='Start time of the attributes history to export')
@click.option('--end_time', required=False, help='End time of the attributes history to export')

def export_devices_attributes_history(path, device_id, device_type_id, device_group_id, include_sub_groups, start_time, end_time):
    
    access_token = get_access_token()
    
    get_devices(access_token, 1, device_id, device_type_id, device_group_id, include_sub_groups)
    log_info(devices)
    
    total_devices = len(devices)
    click.echo(f"找到 {len(devices)} 个设备")
    with tqdm(total=total_devices, desc="Processing devices", unit="device") as pbar:
        for device in devices:
            
            attributes = get_device_attributes(access_token, device['id'])
            time.sleep(1)
            for attribute in attributes:
                attr_identifier = attribute['identifier']
                attr_model = attribute.get('model', {})
                attr_name = attr_model.get('name', '')
                log_info(f"属性 [{attr_identifier} - {attr_name}]")
                pbar.refresh()
                if attr_name and attr_identifier:
                    series_page = 1
                    while True:
                        series_data = get_device_attribute_series(access_token, device['id'], attr_identifier, series_page, start_time, end_time)
                        log_info(series_data)
                        pbar.refresh()
                        for item in series_data:
                            data = [device['name'], device['type_name'], attr_name, item['name'], item['timestamp'],  item['value']]
                            append_to_csv(data)
                        time.sleep(1)
                        if len(series_data) < series_page_records:
                            break
                        series_page += 1
            
            pbar.update(1)  # 更新进度条
            


def get_devices(access_token, page, device_id, device_type_id, device_group_id, include_sub_groups):
    global devices
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    if device_id:
        click.echo(f"正在导出设备 {device_id} 的属性历史记录")
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
        if device_type_id:
            query['type'] = device_type_id
            click.echo(f"正在导出设备类型 {device_type_id} 的属性历史记录")
        elif device_group_id:
            query['groups'] = device_group_id
            if include_sub_groups:
                query['include_sub_groups'] = '1'
            click.echo(f"正在导出设备组 {device_group_id} 的属性历史记录")

        api_url = base_url() + "/api/v1/devices?" + urlencode(query)
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data['result']:
                for device in data['info']['items']:
                    log_info(f"设备 [{device['id']} - {device['name']}]")
                    type_info = device.get('type_info', {})
                    devices.append({
                        'id': device['id'],
                        'name': device['name'],
                        'type_name': type_info.get('name', ''),
                    })
                page_total = data['info']['page_total']
                if page_total > page:
                    time.sleep(1)
                    get_devices(access_token, page+1, device_id, device_group_id, device_type_id)
                        
            else:
                print(f"请求失败！返回结果: {response.json()}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {str(e)}")

def get_device_attributes(access_token, device_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    api_url = base_url() + "/api/v1/device/" + str(device_id) + "/attributes"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['result']:
            return data['info']
        else:
            print(f"请求失败！返回结果: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")


    
def get_device_attribute_series(access_token, device_id, attr_identifier, page, start_ts, end_ts):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    if start_ts is None:
        start_ts = int((time.time() - 30 * 24 * 60 * 60) * 1000)
    if end_ts is None:
        end_ts = int(time.time() * 1000)
    query = {
        'page_records': series_page_records,
        'page': page,
        'start_time': start_ts,
        'end_time': end_ts,
    }
    api_url = base_url() + "/api/v1/device/" + str(device_id) + "/attribute/" + attr_identifier + "/series?" + urlencode(query)
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['result']:
            return data['info']
        else:
            print(f"请求失败！返回结果: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")

def append_to_csv(data):
    with open(f'export/{current_time}.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

