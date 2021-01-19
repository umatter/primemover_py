"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior.
"""
from bs4 import BeautifulSoup
from lxml import etree
from src.worker.Utilities import extract_domain

ParserDict = {}
htmlparser = etree.HTMLParser()


def GoogleParser(behaviors, raw_html):
    term = None
    for b in behaviors:
        if b['name'] == 'text':
            term = b['value']
    if raw_html is None:
        return {'issue': 'unknown', 'term': term}

    if 'captcha' in str(raw_html[0]):
        print('Captcha!')
        return {'issue': 'Captcha', 'term': term}

    soup = BeautifulSoup(raw_html[0], "html.parser")
    results_in = soup.find_all(class_='g')
    if len(results_in) ==0:
        results_in = soup.find_all(class_='rc')

    parsed_data = []
    for rank, result in enumerate(results_in):
        try: url = result.find('a').get('href')
        except:
            url = ''
            print('URL is missing')
        try: domain = extract_domain(url)
        except:
            domain = ''

        try: title = result.find('h3').text
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


def BrowserLeaksParser(behaviors, reports):
    if reports is None:
        return {'issue': 'unknown'}
    parsed_data = []
    for report in reports:
        parsed_data.append(report['pawth'])
    if len(parsed_data) == 0:
        parsed_data = parsed_data[0]
    return parsed_data


ParserDict['GoogleSearch'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political_media_no_utility'] = {
    'method': GoogleParser, 'data': 'html'}
ParserDict['search_google_political_no_utility'] = {'method': GoogleParser,
                                                    'data': 'html'}
ParserDict['search_google_neutral'] = {'method': GoogleParser, 'data': 'html'}
ParserDict['BrowserLeaks'] = {'method': BrowserLeaksParser, 'data': 'reports'}
