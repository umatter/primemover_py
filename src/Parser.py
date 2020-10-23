"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior.
"""
from bs4 import BeautifulSoup
from src.worker.Utilities import extract_domain

ParserDict = {}


def GoogleParser(behaviors, raw_html):
    term = None
    for b in behaviors:
        if b['name'] == 'text':
            term = b['value']
    soup = BeautifulSoup(raw_html[0], "html.parser")
    results_in = soup.find_all(class_='rc')
    parsed_data = []
    for rank, result in enumerate(results_in):
        url = result.find('a').get('href')
        domain = extract_domain(url)
        title = result.find('h3').text
        try: body = result.find(class_='IsZvec').text
        except:
            body = ''

        parsed_data.append({'rank':rank,'term':term, 'title': title, 'url': url, 'body': body,
                            'domain': domain})

    return parsed_data


ParserDict['GoogleSearch'] = GoogleParser
ParserDict['search_google_political'] = GoogleParser
ParserDict['search_google_political_media_no_utility'] = GoogleParser
ParserDict['search_google_politica_no_utility'] = GoogleParser
ParserDict['search_google_neutral'] = GoogleParser


