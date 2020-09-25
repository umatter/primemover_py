def EscapeStrings(text):
    if type(text) is not str:
        raise TypeError('Expected str')
    text = text.replace("/", "\/")
    return text


def new_key(dictionary):
    key = len(dictionary)
    while key in dictionary.keys():
        key += 1
    return key
