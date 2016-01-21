import re

hashtag_regex = re.compile(r'\B#\w*[a-zA-Z]+\w*')
mentions_regex = re.compile(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))'
                            '@([A-Za-z]+[A-Za-z0-9]+)')
links_regex = re.compile('https?:\/\/([\da-z\.-]+)\.'
                         '([a-z\.]{2,6})([\/\w \.-]*)*\/?')

regexs = [hashtag_regex, mentions_regex, links_regex]


def process_text(text):
    for regex in regexs:
        text = regex.sub('', text)
    return text
