"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior.
"""
from bs4 import BeautifulSoup
from src.worker.Utilities import extract_domain

ParserDict = {}


def GoogleParser(raw_html):
    soup = BeautifulSoup(raw_html[0], "html.parser")
    results_in = soup.find_all(class_='rc')
    parsed_data = []
    for result in results_in:
        url = result.find('a').get('href')
        domain = extract_domain(url)
        title = result.find('h3').text
        body = result.find(class_='IsZvec').text

        parsed_data.append({'title': title, 'url': url, 'body': body,
                            'domain': domain})

    return parsed_data


ParserDict['GoogleSearch'] = GoogleParser
