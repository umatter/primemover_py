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
