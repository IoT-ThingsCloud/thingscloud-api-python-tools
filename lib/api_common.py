import configparser
import requests
import json
from lib.logger import log_info

def base_url():
    config = configparser.ConfigParser()
    config.read('config/project_api.ini')
    base_url = config.get('API', 'base_url')
    return base_url


def get_access_token():
    config = configparser.ConfigParser()
    config.read('config/project_api.ini')
    app_id = config.get('API', 'app_id')
    access_key = config.get('API', 'access_key')
    secret_key = config.get('API', 'secret_key')
    auth_payload = {
        'app_id': app_id,
        'access_key': access_key,
        'secret_key': secret_key
    }
    api_auth_url = base_url() + "/api/v1/access_token"
    try:
        response = requests.post(api_auth_url, json=auth_payload)
        response.raise_for_status()
        log_info(f"get_access_token -> {str(response.json())}")
        data = response.json()
        if data['result']:
            return data['info']['access_token']
        return ""
    except requests.exceptions.RequestException as e:
        print(f"获取 AccessToken 时发生错误: {str(e)}")
        return None
