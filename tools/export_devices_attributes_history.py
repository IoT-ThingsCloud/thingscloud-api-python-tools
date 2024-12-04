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
@click.option('--device_id', required=False, help='指定导出数据的设备 ID')
@click.option('--type_id', required=False, help='指定导出数据的设备类型 ID')
@click.option('--group_id', required=False, help='指定导出数据的设备组 ID，支持多个 ID 通过逗号分隔')
@click.option('--include_sub_groups', is_flag=True, required=False, default=False, help='是否包含子组的设备')
@click.option('--start_time', required=False, help='历史数据开始时间，格式为：YYYYMMDDHHmmss')
@click.option('--end_time', required=False, help='历史数据结束时间，格式为：YYYYMMDDHHmmss')

def export_devices_attributes_history(device_id, type_id, group_id, include_sub_groups, start_time, end_time):
    
    access_token = get_access_token()
    if access_token == None:
        click.echo("API 身份验证失败，终止程序")
        return
    
    click.echo("API 身份验证成功")
    click.echo(f"开始导出数据到 {export_csv_path()}")
    data_header = ['设备名称', '设备类型', '属性名称', '属性标识符', '上报时间', '属性值']
    append_to_csv(data_header)
    
    get_devices(access_token, 1, device_id, type_id, group_id, include_sub_groups)
    click.echo(f"共找到 {len(devices)} 个设备")
    
    range_start_ts = time.time() - 30 * 24 * 60 * 60
    range_end_ts = time.time()
    if start_time != None:
        range_start_ts = string_to_unix_timestamp(start_time)
    if end_time != None:
        range_end_ts = string_to_unix_timestamp(end_time)
    range_duration = range_end_ts - range_start_ts
    range_days = range_duration / (24 * 60 * 60)
    log_info(f"导出时间范围: {unix_timestamp_to_datetime_str(range_start_ts)} - {unix_timestamp_to_datetime_str(range_end_ts)}")
    
    total_devices = len(devices)
    click.echo(f"找到 {len(devices)} 个设备")
    with tqdm(total=total_devices, desc="总进度", unit="设备") as pbar:
        for device in devices:
            attributes = get_device_attributes(access_token, device['id'])
            time.sleep(1)
            for attribute in attributes:
                attr_identifier = attribute['identifier']
                attr_model = attribute.get('model', {})
                attr_name = attr_model.get('name', '')
                if attr_name == '':
                    break
                log_info(f"开始导出 设备[{device['name']}] 属性[{attr_identifier} - {attr_name}]")
                pbar.refresh()
                if attr_name and attr_identifier:
                    end_ts = range_end_ts
                    while end_ts > range_start_ts:
                        start_ts = end_ts - 24 * 60 * 60 * 30
                        if start_ts < range_start_ts:
                            start_ts = range_start_ts
                        series_page = 1
                        while True:
                            series_data = get_device_attribute_series(access_token, device['id'], attr_identifier, series_page, range_start_ts, range_end_ts)
                            if series_data == None:
                                break
                            if len(series_data) > 0:
                                first_time = series_data[0]['timestamp']
                                last_time = series_data[-1]['timestamp']
                                click.echo(f"\n设备[{device['name']}] 属性[{attr_name}] 读取数据 {len(series_data)} 条，时间范围: {last_time} - {first_time}")
                                pbar.refresh()
                                for item in series_data:
                                    data = [device['name'], device['type_name'], attr_name, item['name'], iso8601_to_datetime_str(item['timestamp']), item['value']]
                                    append_to_csv(data)
                            
                            time.sleep(1.1)
                            if len(series_data) < series_page_records:
                                break
                            series_page += 1
                        end_ts = start_ts
                            
            pbar.update(1)  # 更新进度条
            


def get_devices(access_token, page, device_id, type_id, group_id, include_sub_groups):
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
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")


    
def get_device_attribute_series(access_token, device_id, attr_identifier, page, start_ts, end_ts):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    query = {
        'page_records': series_page_records,
        'page': page,
        'start_time': start_ts * 1000,
        'end_time': end_ts * 1000,
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
            return None

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")

def export_csv_path():
    return f'export/{current_time}.csv'
    
def append_to_csv(data):
    with open(export_csv_path(), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def string_to_unix_timestamp(start_time_str):
    # 将字符串时间解析为 datetime 对象
    start_time = datetime.datetime.strptime(start_time_str, '%Y%m%d%H%M%S')
    
    # 将 datetime 对象转换为 Unix 时间戳（秒）
    unix_timestamp_seconds = time.mktime(start_time.timetuple())
    
    # 将 Unix 时间戳（秒）转换为毫秒，并返回
    return int(unix_timestamp_seconds)

def unix_timestamp_to_datetime_str(ts):
    # 将Unix时间戳（秒数）转换为datetime对象
    dt = datetime.datetime.fromtimestamp(ts)
    
    # 将datetime对象格式化为字符串
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_time

def iso8601_to_datetime_str(iso8601_str):
    # 将ISO 8601时间字符串转换为datetime对象
    dt = datetime.datetime.fromisoformat(iso8601_str.replace('Z', '+00:00'))
    
    # 将datetime对象格式化为自定义格式
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_time