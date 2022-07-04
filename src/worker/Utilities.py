"""
Assortment of usefull functions

J.L. 11.2020
"""
import tldextract


def EscapeStrings(text):
    """
    :param text: string
    :return: text with forward slashes escaped
    """
    if type(text) is not str:
        raise TypeError('Expected str')
    text = text.replace("/", "\/")
    return text


def new_key(dictionary):
    """
    Generate a new, unique integer key for a dictionary
    Arguments:
         dictionary: dict,
    Returns:
         key: int, an integer which is not in dict.keys()
    """
    key = len(dictionary)
    while key in dictionary.keys():
        key += 1
    return key


def extract_domain(url):
    """
    extract domain from a full url using tldextract.
    Arguments:
        url: string, a valid URL, raises TypeError otherwhise
    Returns:
         string, domain
    """
    try:
        split = tldextract.extract(url)
    except TypeError:
        raise TypeError(f'{url} is strange')
    domain = split.domain + '.' + split.suffix
    return domain


def pref_as_dict(pref_object):
    pref_dict = {}
    for item in pref_object:
        pref_dict[item.get('name')] = item.get('value')
    return pref_dict


def string_to_bool(string_in):
    if type(string_in) is bool:
        return string_in
    elif string_in.lower().strip() in ['false', 'no', 'n']:
        return False
    elif string_in.lower().strip() in ['true', 'yes', 'y']:
        return True
    else:
        raise ValueError(f"{string_in} is not a recognized string!")
