"""
Wrapper functions for the primemover s3 bucket.

Available Functions:
    - check_file

J.L. 01.21
"""
import boto3
import json
import pathlib
import io
import os
import zipfile
import botocore.exceptions
import pandas as pd

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

with open(PRIMEMOVER_PATH + "/resources/other/keys.json", 'r') as f:
    KEYS = json.load(f)['S3']

BUCKET_IN_OUT = 'primemover_py'

CLIENT = boto3.client('s3',
                      aws_access_key_id=KEYS['Access_Key_ID'],
                      aws_secret_access_key=KEYS['Secret_Access_Key'],
                      region_name="eu-central-1"
                      )


def fetch_report(job_id: int, report_type='dynamic'):
    """
    fetch job report from s3 bucket:
    """

    report_type = report_type.lower().strip()
    if not report_type in ['dynamic', 'static', 'html']:
        raise ValueError('report type must be one of dynamic, static and html')
    in_stream = io.BytesIO()
    try:
        if report_type == 'html':
            file_path = f"finalsource/{report_type}_jobdata_{job_id}"
        CLIENT.download_fileobj("primemoverrunner",
                                f"reports/{report_type}_jobdata_{job_id}",
                                in_stream,
                                )
        success = True
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == "404":
            success = False
        else:
            raise err

    return in_stream, success


def download_dynamic(job_id):
    raw_data, success = fetch_report(job_id, 'dynamic')
    if success:
        as_zipfile = zipfile.ZipFile(raw_data)
        name = None
        for name in as_zipfile.namelist():
            if 'json' in name:
                break
        raw_json = as_zipfile.read(name)
        raw_dict = json.loads(raw_json)
    else:
        raw_dict = {}
    return raw_dict, success


def check_file(filename, bucket='primemoverpy'):
    resp = CLIENT.list_objects_v2(Bucket=bucket)
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
        if file_path.endswith('.csv'):
            try:
                file_in = pd.read_csv(file_path)
            except UnicodeDecodeError:
                file_in = pd.read_csv(file_path, encoding='latin1')
            file_in.to_csv(file_path, encoding='utf-16', index=False)
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


def fetch_neutral_domains():
    path = "/resources/input_data/neutraldomains_pool.csv"
    return fetch_file(path, "neutraldomains_pool.csv")


def fetch_private(path="/resources/proxies/private_proxies_new.csv"):
    return fetch_file(path, "private_proxies.csv")


def fetch_rotating(path="/resources/proxies/rotating_proxies_new.csv"):
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


def fetch_file_memory(filename):
    """
    fetch file from s3 bucket:

    """

    in_stream = io.BytesIO()

    try:
        CLIENT.download_fileobj("primemoverpy", filename, in_stream)
        success = True

    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == "404":
            success = False
        else:
            raise err
    return success, in_stream


def push_dict(filename, to_push):
    """
    fetch file from s3 bucket:

    """

    out_stream = io.BytesIO()
    out_stream.write(json.dumps(to_push).encode())
    out_stream.seek(0)
    response = CLIENT.upload_fileobj(out_stream, 'primemoverpy', filename)
    return 'success'


def append_csv(filename, data):
    # If file exists on s3, download and append
    temp_path = f"/resources/temp/{filename.replace('/', '_')}"
    path = PRIMEMOVER_PATH + temp_path
    if check_file(filename):

        try:
            fetch_file(temp_path, filename)
        except pd.errors.EmptyDataError:
            print(Exception)
            data.to_csv(path)

        data.to_csv(path, mode='a', header=False)
    else:
        data.to_csv(path)

    response = upload_data(filename, temp_path)
    os.remove(path)
    return response
