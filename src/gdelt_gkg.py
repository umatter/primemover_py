import pandas as pd
import collections
import difflib
import json
import os

from src.gdelt_url_country import get_country_media

IN_COUNTRY_MEDIA = ['resources/other/', '_urls.json']

COL_NAMES = ['GKGRECORDID',
             'DATE',
             'SourceCollectionIdentifier',
             'SourceCommonName',
             'DocumentIdentifier',
             'Counts',
             'V2Counts',
             'Themes',
             'V2Themes',
             'Locations',
             'V2Locations',
             'Persons',
             'V2Persons',
             'Organizations',
             'V2Organizations',
             'V2Tone',
             'Dates',
             'GCAM',
             'SharingImage',
             'RelatedImages',
             'SocialImageEmbeds',
             'SocialVideoEmbeds',
             'Quotations',
             'AllNames',
             'Amounts',
             'TranslationInfo',
             'Extras']

RELEVANT_COLL_NAMES = ['GKGRECORDID',
                       'DATE',
                       'SourceCommonName',
                       'Themes',
                       'V2Themes',
                       'Locations',
                       'V2Locations',
                       'Persons',
                       'V2Persons',
                       'Organizations',
                       'V2Organizations',
                       'V2Tone',
                       'Quotations',
                       'AllNames',
                       ]

REMOVE = ['United States', 'United Kingdom']

GDELTV2_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

OUT_PATH = 'resources/other/individuals.json'

with open('resources/other/useless_org.json', 'r') as file:
    LIBRARY_OF_USELESS = json.load(file)


def method_persons(name, dict_name, nr_first, nr_second, freq_lim=10):
    terms = []
    related_1 = collections.Counter(dict_name[name]['with_name'])
    for related_name_1, freq_1 in related_1.most_common(nr_first):
        if freq_1 <= freq_lim:
            continue
        related_2 = collections.Counter(dict_name[related_name_1]['with_name'])
        intersection_1_2 = set(related_1).intersection(set(related_2))
        related_2 = collections.Counter(
            {n: f for n, f in related_2.items() if n in intersection_1_2})

        for related_name_2, freq_2 in related_2.most_common(nr_second):
            if freq_2 <= freq_lim:
                continue
            terms.append({name, related_name_1})
    return terms


def method_org(name, dict_name, nr_first, freq_lim=10):
    terms = []
    filtered_org = []
    for org in dict_name[name]['with_org']:
        if org not in LIBRARY_OF_USELESS:
            filtered_org.append(org)

    related_org = collections.Counter(filtered_org)
    for org, freq in related_org.most_common(nr_first):
        if freq <= freq_lim:
            continue
        terms.append([name, org])
    return terms


def load_gkg(hours=12, country='US'):
    country_media_path = IN_COUNTRY_MEDIA[0] + country + IN_COUNTRY_MEDIA[1]
    if not os.path.exists(country_media_path):
        get_country_media(country)

    with open(country_media_path, 'r') as file:
        country_media = json.load(file)

    list_urls = pd.read_csv(GDELTV2_URL, sep=' ', names=['idx', 'smth', 'url'],
                            low_memory=False)
    gkg = list_urls.iloc[2::3, 2].tolist()
    nr = 4 * hours
    last_12_hours = gkg[-nr:]
    raw_gkg = pd.DataFrame(columns=RELEVANT_COLL_NAMES)
    for url in last_12_hours:
        raw_gkg = raw_gkg.append(pd.read_csv(url,
                                             sep='\t',
                                             lineterminator='\n',
                                             low_memory=False,
                                             names=COL_NAMES,
                                             usecols=RELEVANT_COLL_NAMES,
                                             dtype={'AllNames': 'str'},
                                             parse_dates=['DATE']),
                                 ignore_index=True)
    raw_gkg = raw_gkg.loc[raw_gkg.SourceCommonName.isin(country_media)]
    return raw_gkg


def frequent_names(nr, raw_gkg, org=False, sim_cut_of=0.9):
    all_names_dict = {}
    non_empty = raw_gkg.dropna(subset=['V2Persons', 'Organizations'])
    for r_i in non_empty.index:
        all_names_and_loc = non_empty.loc[r_i]['V2Persons'].split(';')

        org = non_empty.loc[r_i]['Organizations'].split(';')
        if len(set(org).intersection({'instagram', 'national sports query',
                                      'sports format local national mix',
                                      'olympics',
                                      'heartradio national jingle day',
                                      'youtube', 'inferno national promotions',
                                      'sports format national'})) >= 3:
            continue

        names = set()
        for name_and_loc in all_names_and_loc:
            name = name_and_loc.split(',')[0]
            val = all_names_dict.get(name, {'freq': 0})['freq']
            if val == 0:
                all_names_dict[name] = {'freq': 0, 'with_name': [],
                                        'with_org': []}
            all_names_dict[name]['freq'] = val + 1
            names.add(name)

        for n_j, name in enumerate(names):
            filtered_names = set()
            for n in names:
                not_similar = difflib.SequenceMatcher(None, name,
                                                      n).ratio() < sim_cut_of
                if not_similar and n not in REMOVE:
                    filtered_names.add(n)
            all_names_dict[name]['with_name'] = all_names_dict[name][
                                                    'with_name'] + list(
                filtered_names)
            all_names_dict[name]['with_org'] = all_names_dict[name][
                                                   'with_org'] + list(org)

    all_names = pd.DataFrame.from_dict(all_names_dict).T
    all_names.sort_values(by='freq', ascending=False, inplace=True)
    all_names.reset_index(drop=False, inplace=True)
    all_names.rename(columns={'index': 'name'}, inplace=True)
    all_names = all_names[0:nr]

    search_terms = []
    for n in all_names['name']:
        if not org:
            search_terms.extend(method_persons(n, all_names_dict, 10, 2, 1))
        else:
            search_terms.extend(method_org(n, all_names_dict, 1, 10))
    search_terms_rm_dup = []
    for term in search_terms:
        if term not in search_terms_rm_dup:
            search_terms_rm_dup.append(term)

    return search_terms_rm_dup


def main(nr_results, org=True):
    data = load_gkg(12, 'US')
    name_comb = frequent_names(nr_results, data, org)
    search_terms = []
    for name_set in name_comb:
        search_terms.append(' '.join(name_set))
    with open(OUT_PATH, 'w') as out:
        json.dump(search_terms, out, separators=(',\n', ':'))


if __name__ == "__main__":
    main(30)
