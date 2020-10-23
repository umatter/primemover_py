import pandas as pd
from datetime import date
import json
import random

IN_PATH = 'resources/other/Raw_Media_Headers.csv'
COL_NAMES = ['term_params',
             'date_scraped',
             'source',
             'domain'
             'political_orientation']
OUT_PATH = {'right': 'Data/terms/right_terms.json',
            'left': 'resources/other/left_terms.json',
            'benign': 'resources/other/benign_terms.json'}

DELETE_TERMS = ['Video:', 'Breaking:', 'Watch: ']


def clean_token(token):
    """ Return a version of string str in which all letters have been
    converted to lowercase and punctuation characters have been stripped
    from both ends. Inner punctuation is left untouched. """
    punctuation = '''!"'`’‘,;:-?)([]<>*#'''
    token = token.strip(punctuation)
    return token


def clean_header(header):
    header = header.replace('\n', ' ')
    header = header.replace('\r', ' ')
    header = header.replace('\t', ' ')
    header = header.replace('.', '')
    header = header.lower()
    tokens = header.split(' ')
    result = ''
    for token in tokens:
        result = result + clean_token(token) + ' '

    return result.strip()


def GenerateSearchTerms(in_path=IN_PATH):
    today = pd.Timestamp(date.today())
    headers = pd.read_csv(IN_PATH, header=0, parse_dates=['date_scraped'])
    headers = headers.loc[headers['date_scraped'] == today]
    terms = {'right': [], 'left': []}
    for row in headers.itertuples():
        term = clean_header(row.search_term)
        terms[row.political_orientation] = \
            terms[row.political_orientation] + \
            [{'term': term, 'choice_type': 'domain', 'choice_param': row.domain, 'type': 'political'}]
    with open(OUT_PATH['right'], 'w') as jar:
        json.dump(terms['right'], jar)

    with open(OUT_PATH['left'], 'w') as jar:
        json.dump(terms['left'], jar)


def conversion():
    units = {'fluid': ['ounces', 'liters', 'ml', 'tbsps', 'tsps', 'gallons'],
             'weight': ['pounds', 'kilos', 'grams', 'ounces', 'tons', 'ounces'],
             'distance': ['miles', 'nautical miles', 'inches', 'feet', 'cm', 'mm',
                          'meters', 'kilometers', 'light years'],
             'currency': ['yen', 'dollars', 'euros', 'swiss franc',
                          'rupee', 'singapore dollars', 'dirham',
                          'australian dollars', 'pounds', 'turkish lyra',
                          'kroner', 'pesos']}
    field = random.choice(['fluid', 'weight', 'distance'])
    unit_1, unit_2 = random.sample(units[field], k=2)
    nr = random.randint(1, 10)
    connect = random.choice(['is', 'are'])
    return f'what {connect} {nr} {unit_1} in {unit_2}'


def equation():
    operations = ['+','-','/']
    nr_op = random.randint(1, 3)
    ops = random.choices(operations, k=nr_op)
    eq = str(random.randint(1, 1000))
    for op in ops:
        eq = eq + op + str(random.randint(1, 10000))
    return eq


def GenerateBenignTerms():
    with open('resources/other/common.json', 'r') as file:
        common_terms = json.load(file)
    file.close()

    with open('resources/other/countries.json', 'r') as file:
        countries = json.load(file)
    file.close()

    country_modifiers = ['population', 'neighbouring countries', 'GDP',
                         'GDP per capita', 'culture',
                         'people', 'sports', 'history']
    terms = []
    for term in common_terms:
        terms.append(term)
    country_terms = random.sample(countries, k=15)
    for country in country_terms:
        mod = random.choice(country_modifiers)
        terms.append(f'{country} {mod}')
    for i in range(1, 15):
        terms.append(conversion())

    for i in range(1, 10):
        terms.append(equation())

    with open(OUT_PATH['benign'], 'w') as jar:
        json.dump(terms, jar)


if __name__ == "__main__":
    GenerateBenignTerms()
