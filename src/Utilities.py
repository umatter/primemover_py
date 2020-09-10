def EscapeStrings(text):
    if type(text) is not str:
        raise TypeError('Expected str')
    text = text.replace("/", "\/")
    return text
