"""
For all tasks that gather data which needs to be extracted from a raw HTML file,
define a parser function. Store all function names in a dictionary, with keys the
Task name as specified in a TaskBehavior. The parsing functions contained here are
intended to be used in conjunction with Results.py. Extend parsers by defining new
parsing functions and adding these to a dictionary as seen here and in src_google/worker/google_s3_parser.
"""
from lxml import etree
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())

ParserDict = {}
htmlparser = etree.HTMLParser()

UpdateParser = {}


def CaptchaParser(behaviors, raw_html, job_id):
    """
    Search HTML file for references to captchas
    Arguments:
        - raw_html: html file to parse
        - job_id: int, job_id assigned by the primemover_api
    Returns:
        dict, key: issue, value: Captcha if a reference is found, no_captcha if there is none,
    """
    if raw_html is None:
        return {'issue': 'unknown'}

    if 'captcha' in str(raw_html):
        print(f'Captcha: {job_id}')
        return {'issue': 'Captcha'}
    return {'issue': 'no captcha'}


def BrowserLeaksParser(behaviors, reports, job_id):
    """
        pre-proccess browser leaks reports (May be redundant with new s3 format)
    """
    if reports is None:
        return {'issue': 'unknown'}
    parsed_data = []
    for report in reports:
        parsed_data.append(report['path'])
    if len(parsed_data) == 0:
        parsed_data = parsed_data[0]
    return parsed_data

# Define parser dictionaries. The idea is the following, there are different elements of
# a report one may be interested in. Each ParserDict contains the functions defined in this file one is currently interested
# in for each tag denoted in a given job.

ParserDict['leak_ip'] = {'method': BrowserLeaksParser, 'data': 'reports'}
ParserDict['leak_javascript'] = {'method': BrowserLeaksParser,
                                 'data': 'reports'}
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
