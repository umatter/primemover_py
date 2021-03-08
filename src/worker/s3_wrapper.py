"""
Wrapper functions for the primemover s3 wrapper.

Available Functions:
    - check_file

J.L. 01.21
"""
import boto3
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

with open(PRIMEMOVER_PATH + "/resources/other/keys.json", 'r') as f:
    KEYS = json.load(f)['S3']

BUCKET = 'primemover_py'

CLIENT = boto3.client('s3',
                      aws_access_key_id=KEYS['Access_Key_ID'],
                      aws_secret_access_key=KEYS['Secret_Access_Key'],
                      region_name="eu-central-1"
                      )


def check_file(filename):
    resp = CLIENT.list_objects_v2(Bucket='primemoverpy')
    exists = False
    for obj in resp.get('Contents'):
        if obj['Key'] == filename:
            exists = True
            break
    return exists


def list_files():
    resp = CLIENT.list_objects_v2(Bucket='primemoverpy')
    files = []
    for obj in resp.get('Contents'):
        files.append(obj['Key'])
    return files


def fetch_file(path, filename):
    if check_file(filename):
        file_path = PRIMEMOVER_PATH + path
        CLIENT.download_file("primemoverpy", filename, file_path)
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            print(f'File has been stored at {path}')
            data = None
    else:
        raise FileExistsError(
            f'The file {filename} is not available in the bucket')
    return data


def fetch_neutral():
    """
    fetch neural_terms
    """
    path = "/resources/input_data/neutral_searchterms_pool.json"
    return fetch_file(path, "neutral_searchterms_pool.json")


def fetch_terms():
    path = "/resources/input_data/searchterms_pool.csv"
    return fetch_file(path, "searchterms_pool.csv")


def fetch_outlets():
    path = "/resources/input_data/outlets_pool.csv"
    return fetch_file(path, "outlets_pool.csv")


def fetch_private():
    path = "/resources/proxies/private_proxies.csv"
    return fetch_file(path, "private_proxies.csv")


def fetch_rotating():
    path = "/resources/proxies/rotating_proxies.csv"
    return fetch_file(path, "rotating_proxies.csv")


def fetch_private_json():
    path = "/resources/proxies/private_proxies.json"
    return fetch_file(path, "private_proxies.json")


def fetch_rotating_json():
    path = "/resources/proxies/rotating_proxies.json"
    return fetch_file(path, "rotating_proxies.json")


def fetch_geosurf():
    path = "/resources/proxies/geosurf_proxies.csv"
    return fetch_file(path, "geosurf_proxies.csv")


def fetch_geosurf_json():
    path = "/resources/proxies/geosurf.json"
    return fetch_file(path, "geosurf.json")


def fetch_proxy_rotating_update():
    path = "/resources/proxies/rotating_proxies_updates.json"
    return fetch_file(path, "rotating_proxies_updates.json")


def fetch_proxy_private_update():
    path = "/resources/proxies/private_proxies_updates.json"
    return fetch_file(path, "private_proxies_updates.json")


def create_directory(directory_name):
    check_file(directory_name)
    CLIENT.put_object(Bucket='primemoverpy', Key=(directory_name + '/'))


def upload_data(filename, path):
    file_path = PRIMEMOVER_PATH + path
    check_file(filename)

    response = CLIENT.upload_file(Filename=file_path, Bucket='primemoverpy',
                                  Key=filename)
    return response


def fetch_valid_cities():
    path = '/resources/other/valid_cities.json'
    return fetch_file(path, "valid_cities.json")


def update_valid_cities():
    path = '/resources/other/valid_cities.json'
    file_path = PRIMEMOVER_PATH + path
    locations = fetch_valid_cities()
    locations.update(fetch_private_json())
    locations.update(fetch_rotating_json())
    with open(file_path, 'w') as f:
        json.dump(locations, f)
