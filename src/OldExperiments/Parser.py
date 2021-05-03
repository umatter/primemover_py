"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior.
"""
from bs4 import BeautifulSoup
from lxml import etree
from src.worker.Utilities import extract_domain
import pandas as pd
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

ParserDict = {}
htmlparser = etree.HTMLParser()

UpdateParser = {}


def GoogleParser(behaviors, raw_html, job_id):
    term = None
    for b in behaviors:
        if b['name'] == 'text':
            term = b['value']
    if raw_html is None:
        return {'issue': 'unknown', 'term': term}

    if 'captcha' in str(raw_html[0]):
        print(f'Captcha: {job_id}')
        return {'issue': 'Captcha', 'term': term}

    soup = BeautifulSoup(raw_html[0], "html.parser")
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


def BrowserLeaksParser(behaviors, reports, job_id):
    if reports is None:
        return {'issue': 'unknown'}
    parsed_data = []
    for report in reports:
        parsed_data.append(report['path'])
    if len(parsed_data) == 0:
        parsed_data = parsed_data[0]
    return parsed_data




def SelectionParser(behaviors, dynamic_data, job_id):
    if dynamic_data is None:
        return {'issue': 'unknown'}

    path_outlets = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool.csv'
    outlets = pd.read_csv(path_outlets,
                          usecols=['domain', 'redirect_url', 'pi'])
    outlets['pi'] = outlets['pi'].astype(float)

    for result in dynamic_data[0]['items']:
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



ParserDict['GoogleSearch'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political_media_no_utility'] = {
    'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political_no_utility'] = {'method': GoogleParser,
                                                    'data': 'html'}
ParserDict['search_google_neutral'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['BrowserLeaks'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['CALCULATED/search_google_neutral'] = {'method': SelectionParser,
                                                  'data': 'dynamic'}

UpdateParser['CALCULATED/search_google_neutral'] = {'method': SelectionParser,
                                                    'data': 'dynamic'}
ParserDict['CA'] = {'method': GoogleParser, 'data': 'html'}
