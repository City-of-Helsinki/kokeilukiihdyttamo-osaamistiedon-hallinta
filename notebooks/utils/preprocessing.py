import string
import re
from voikko import libvoikko
from functools import partial

PUNCT = list(string.punctuation) + ['–', '”', '•']

def remove_punct(tokens: [str]) -> [str]:
    return [t for t in tokens if t not in PUNCT]


table = str.maketrans({c: f' {c} ' for c in PUNCT})

def tokenize(s: str) -> [str]:
    return s.translate(table).strip().split()


def replace_url(s: str, replace_string='HTTP') -> str:

    def is_url(token):
        prefixes = ('http://', 'https://', 'www.')
        return token.startswith(prefixes)

    return ' '.join([replace_string if is_url(t) else t for t in s.split()])

v = libvoikko.Voikko('fi')

def voikko_lemmatize(s: str) -> str:
    info = v.analyze(s)
    
    if len(info) > 0:
        # TODO: is there some better heuristic than [0]?
        return info[0]['BASEFORM'].lower()
    
    return s

def apply_lemmatize(lemmatize_func, tokens: [str]) -> [str]:
    return [lemmatize_func(t) for t in tokens]

def id_func(x):
    return x

def _preprocess_func(s, lemmatize):
    _lemmatize_func = voikko_lemmatize if lemmatize else id_func
    
    funcs = [
        lambda s: s.lower(),
        replace_url,
        tokenize,
        remove_punct,
        lambda tokens: [_lemmatize_func(t) for t in tokens],
        lambda tokens: ' '.join(tokens)
    ]
    
    for f in funcs:
        s = f(s)
        
    return s

def preprocess_func(lemmatize):
    return partial(_preprocess_func, lemmatize=lemmatize)