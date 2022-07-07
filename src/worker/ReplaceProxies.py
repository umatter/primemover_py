"""
Takes new and old proxy list and finds best match for replaced proxies.
"""
import src.worker.s3_wrapper as s3
import pathlib
import os
import pandas as pd

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


def update_proxies(proxy_type='rotating'):
    # Check if files exist and fetch otherwhise.
    proxy_type = proxy_type.lower().strip()
    if proxy_type not in ["rotating", "private", "p", "r"]:
        raise NotImplementedError(
            "Expected either rotating (r) or private (p) as proxy job_type.")
    if proxy_type in ["rotating", "r"]:
        existing_path = PRIMEMOVER_PATH + "/resources/proxies/rotating_proxies.csv"
        new_path = PRIMEMOVER_PATH + "/resources/proxies/rotating_proxies_new.csv"
    else:
        existing_path = PRIMEMOVER_PATH + "/resources/proxies/private_proxies.csv"
        new_path = PRIMEMOVER_PATH + "/resources/proxies/private_proxies_new.csv"
    if not os.path.exists(existing_path):
        raise FileNotFoundError(
            f'Expected file {existing_path} to exist. Call initialize_proxy_csv if no proxies are currently in use.')
    if not os.path.exists(new_path):
        if proxy_type in ["rotating", "r"]:
            s3.fetch_rotating()
        else:
            s3.fetch_private()
    in_proxies = pd.read_csv(new_path)
    new_proxies = in_proxies.loc[in_proxies['active'] == 1][
        ['provider', 'gateway_ip', 'gateway_ip_port', 'ip', 'job_type',
         'country_code', 'country_name', 'region_code', 'region_name', 'city',
         'zip', 'lat', 'long', 'geoname_id', 'time_zone_id',
         'time_zone_code', 'proxy_asn', 'proxy_isp', 'loc_id',
         'active']]
    existing_proxies = pd.read_csv(existing_path)
    existing_proxies = existing_proxies.loc[existing_proxies['active'] == 1][
        ['provider', 'gateway_ip', 'gateway_ip_port', 'ip', 'job_type',
         'country_code', 'country_name', 'region_code', 'region_name', 'city',
         'zip', 'lat', 'long', 'geoname_id', 'time_zone_id',
         'time_zone_code', 'proxy_asn', 'proxy_isp', 'loc_id',
         'active']]
    existing_proxies['active'] = 0

    combined = existing_proxies.merge(new_proxies, how='outer',
                                      on=['provider', 'gateway_ip',
                                          'gateway_ip_port', 'ip', 'job_type',
                                          'proxy_asn',
                                          'proxy_isp'
                                          ], suffixes=(None, "_new"))
    update_dict = {}
    matched = combined[~combined.active.eq(1) & combined.active_new.eq(1)]
    # If anything at all changes despite the proxy remaining identical, add an
    # 'empty'
    for i in range(len(matched)):
        if not matched.loc[i]['loc_id'] == matched.loc[i]['loc_id_new']:
            update_dict[
                f'{matched.loc[i]["gateway_ip"]}:{matched.loc[i]["gateway_ip_port"]}'] = {
                'host': str(matched.loc[i]["gateway_ip"]),
                'port': str(matched.loc[i]["gateway_ip_port"]),
                'provider': str(matched.loc[i]["provider"]),
                'old_location': str(matched.loc[i]["loc_id"]),
                'new_location': str(matched.loc[i]["loc_id_new"])
            }

    un_matched = combined[~combined.active.eq(0) | combined.active_new.eq(0)]
    if len(un_matched) != 0:
        raise Exception("something is wrong with the proxies!! pls fix")

    in_proxies.to_csv(existing_path, index=False)

    return update_dict


def update_all_proxies():
    s3.update_valid_cities()
    update_dict = update_proxies('private')
    update_dict.update(update_proxies('rotating'))

    return update_dict
