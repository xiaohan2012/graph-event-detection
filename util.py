import codecs
import ujson as json
import math
import gensim
import collections
import functools

from datetime import datetime
from collections import defaultdict


def load_items_by_line(path):
    with codecs.open(path, 'r', 'utf8') as f:
        items = set([l.strip()
                    for l in f])
    return items


def load_json_by_line(path):
    return map(json.loads, load_items_by_line(path))


def load_id2obj_dict(path, id_key):
    try:
        interactions = json.load(open(path))
    except ValueError:
        interactions = load_json_by_line(path)
    d = defaultdict(lambda: {'id': 'unknown', 'name': 'unknown'})
    for i in interactions:
        d[i[id_key]] = i
    return d


def get_datetime(obj):
    if isinstance(obj, datetime):
        return obj
    elif (isinstance(obj, float) or
          isinstance(obj, int)) and not math.isnan(obj):
        return datetime.fromtimestamp(obj)
    elif isinstance(obj, long):
        return datetime.fromtimestamp(obj / 1000)
    elif isinstance(obj, basestring):
        patterns = ['%Y-%m-%d %X.%f', '%Y-%m-%d %X']
        ok = False
        for p in patterns:
            try:
                dt = datetime.strptime(
                    obj, p
                )
                ok = True
            except ValueError:
                continue
        if ok:
            return dt
        else:
            raise ValueError('Bad datetime format for {}'.format(patterns))
    else:
        raise TypeError('Unacceptable type {}, {}'.format(type(obj), obj))


def compose(*functions):
    def inner(arg):
        for f in functions:
            arg = f(arg)
        return arg
    return inner


def json_dump(obj, path):
    with codecs.open(path, 'w', 'utf8') as f:
        f.write(json.dumps(obj))


def json_load(path):
    with codecs.open(path, 'r', 'utf8') as f:
        return json.load(f)


def load_summary_related_data(interactions_path, people_path,
                              corpus_dict_path, lda_model_path):
    interactions = json.load(open(interactions_path))
    people_info = json.load(open(people_path))

    dictionary = gensim.corpora.dictionary.Dictionary.load(
        corpus_dict_path
    )
    lda = gensim.models.ldamodel.LdaModel.load(
        lda_model_path
    )
    return interactions, people_info, dictionary, lda


class memoized(object):
    """
    Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring.
        """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods.
        """
        return functools.partial(self.__call__, obj)
