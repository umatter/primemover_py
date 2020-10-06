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
    :param dictionary: dict,
    :return key: int, an integer which is not in dict.keys()
    """
    key = len(dictionary)
    while key in dictionary.keys():
        key += 1
    return key


def extract_domain(url):
    """
    :param url:
    :return: domain
    """
    try:
        split = tldextract.extract(url)
    except TypeError:
        raise TypeError(f'{url} is strange')
    domain = split.domain + '.' + split.suffix
    return domain
