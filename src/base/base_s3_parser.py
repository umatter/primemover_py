"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior.
"""
from lxml import etree
import pathlib


PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

ParserDict = {}
htmlparser = etree.HTMLParser()

UpdateParser = {}


def CaptchaParser(behaviors, raw_html, job_id):
    if raw_html is None:
        return {'issue': 'unknown'}

    if 'captcha' in str(raw_html):
        print(f'Captcha: {job_id}')
        return {'issue': 'Captcha'}
    return {'issue':'no captcha'}

def BrowserLeaksParser(behaviors, reports, job_id):
    if reports is None:
        return {'issue': 'unknown'}
    parsed_data = []
    for report in reports:
        parsed_data.append(report['path'])
    if len(parsed_data) == 0:
        parsed_data = parsed_data[0]
    return parsed_data


ParserDict['leak_ip'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_javascript'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_webrtc'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_canvas'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_webgl'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_fonts'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_ssl'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_features'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_proxy'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_java'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_flash'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_ssl'] = {'method': BrowserLeaksParser, 'data': 'reports'}

ParserDict['captcha'] = {'method': CaptchaParser, 'data': 'html'}
