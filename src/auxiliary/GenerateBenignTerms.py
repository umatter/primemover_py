"""
Generate benign Terms

J.L. 11.2020
"""

import json
import random
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())
IN_PATH = PRIMEMOVER_PATH + '/resources/other/Raw_Media_Headers.csv'
COL_NAMES = ['term_params',
             'date_scraped',
             'source',
             'domain'
             'political_orientation']
OUT_PATH = {'benign': PRIMEMOVER_PATH + '/resources/other/benign_terms.json'}


def conversion():
    units = {'fluid': ['ounces', 'liters', 'ml', 'tbsps', 'tsps', 'gallons'],
             'weight': ['pounds', 'kilos', 'grams', 'ounces', 'tons', 'ounces'],
             'distance': ['miles', 'nautical miles', 'inches', 'feet', 'cm',
                          'mm',
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
    operations = ['+', '-', '/']
    nr_op = random.randint(1, 3)
    ops = random.choices(operations, k=nr_op)
    eq = str(random.randint(1, 1000))
    for op in ops:
        eq = eq + op + str(random.randint(1, 10000))
    return eq


def GenerateBenignTerms():
    with open(PRIMEMOVER_PATH + '/resources/other/common.json', 'r') as file:
        common_terms = json.load(file)
    file.close()

    with open(PRIMEMOVER_PATH + '/resources/other/countries.json', 'r') as file:
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
    return 'success'


if __name__ == "__main__":
    GenerateBenignTerms()
