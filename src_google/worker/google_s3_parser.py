from src.base.base_s3_parser import *
from src.worker.Utilities import extract_domain
import pandas as pd
from bs4 import BeautifulSoup


def GoogleParser(behaviors, raw_html, job_id):
    term = None
    for b in behaviors:
        if b['name'] == 'text':
            term = b['value']
    if raw_html is None:
        return {'issue': 'unknown', 'term': term}

    if 'captcha' in str(raw_html):
        print(f'Captcha: {job_id} ')
        return {'issue': 'Captcha', 'term': term}

    soup = BeautifulSoup(raw_html, "html.parser")
    results_in = soup.find_all(class_='g')
    if len(results_in) == 0:
        results_in = soup.find_all(class_='rc')

    parsed_data = []
    for rank, result in enumerate(results_in):
        try:
            url = result.find('a').get('href')
        except:
            url = ''
            print('URL is missing')
        try:
            domain = extract_domain(url)
        except:
            domain = ''

        try:
            title = result.find('h3').text
        except:
            title = ''
            # print('Title is missing')
        try:
            body = result.find(class_='IsZvec').text
        except:
            # print('Body is missing')
            body = ''

        parsed_data.append(
            {'rank': rank, 'term': term, 'title': title, 'url': url,
             'body': body,
             'domain': domain})

    return parsed_data


def SelectionParser(behaviors, dynamic_data, job_id):
    if dynamic_data is None:
        return {'issue': 'unknown'}

    path_outlets = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool.csv'
    outlets = pd.read_csv(path_outlets,
                          usecols=['domain', 'redirect_url', 'pi'])
    outlets['pi'] = outlets['pi'].astype(float)

    for result in dynamic_data['items']:
        if result['selected']:
            for row in outlets.index:
                outlet_match = outlets.loc[
                    outlets['domain'] == result['normalizedUrl']]
                if outlet_match.shape[0] > 1:
                    if outlet_match.loc[
                        outlets['redirect_url'] == result['url']].shape[0] > 0:
                        outlet_match = outlet_match.loc[
                            outlets['redirect_url'] == result['url']]
                if outlet_match.shape[0] >= 1:
                    outlet_match = outlet_match.iloc[0]
                else:
                    continue

                return {'url': outlet_match['redirect_url'],
                        'domain': result['normalizedUrl'],
                        'pi': outlet_match['pi'], 'known': result['known']}
            else:
                return (
                    {'url': result['url'], 'domain': result['normalizedUrl'],
                     'pi': None, 'known': False})


ParserDict['google_search'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['political'] = {'method': GoogleParser,
                           'data': 'html'}
ParserDict['neutral'] = {'method': GoogleParser, 'data': 'html'}


ParserDict['CALCULATED/neutral'] = {'method': SelectionParser,
                                                  'data': 'dynamic'}
ParserDict['CALCULATED/political'] = {'method': SelectionParser,
                                                  'data': 'dynamic'}

UpdateParser['CALCULATED/neutral'] = {'method': SelectionParser,
                                                    'data': 'dynamic'}
