"""
Loads list of media outlet urls and their corresponding countries from gdelt and
creates  a json file containing the urls for a specified country.

J.L. 04.2020
"""


import pandas as pd
import json


def get_country_media(c = 'US'):
    OUT_PATH = f'resources/other/{c}_urls.json'

    url_country = pd.read_csv(
        'http://data.gdeltproject.org/blog/2018-news-outlets-by-country-may2018-update/MASTER-GDELTDOMAINSBYCOUNTRY-MAY2018.TXT',
        sep='\t', lineterminator='\n',
        low_memory=False,
        names=['url', 'country_code', 'country_name'])

    desired_urls = url_country.loc[url_country['country_code'] == c][
        'url']

    with open(OUT_PATH, 'w') as tub:
        json.dump(desired_urls.to_list(), tub)


if __name__ == "__main__":
    country = input('which countries media outlets would you like to collect?: ')
    get_country_media(country)
