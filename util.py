import codecs
import ujson as json
from datetime import datetime


def load_items_by_line(path):
    with codecs.open(path, 'r', 'utf8') as f:
        items = set([l.strip()
                    for l in f])
    return items


def load_json_by_line(path):
    return map(json.loads, load_items_by_line(path))


def load_msgid2interaction_dict(path):
    interactions = load_json_by_line(path)
    return {i['message_id']: i
            for i in interactions}


def load_peopleid2people_dict(path):
    people = load_json_by_line(path)
    return {p['id']: p
            for p in people}


def get_datetime(obj):
    if isinstance(obj, datetime):
        return obj
    elif isinstance(obj, float) or isinstance(obj, int):
        return datetime.fromtimestamp(obj)
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


def main():
    import ujson as json
    with open('html/data/id2interaction.json', 'w') as f:
        json.dump(load_msgid2interaction_dict('data/enron.json'), f)

    with open('html/data/id2people.json', 'w') as f:
        json.dump(load_peopleid2people_dict('data/people.json'), f)


def compose(*functions):
    def inner(arg):
        for f in functions:
            arg = f(arg)
        return arg
    return inner


def json_dump(obj, path):
    with codecs.open(path, 'w', 'utf8') as f:
        f.write(json.dumps(obj))

if __name__ == '__main__':
    main()

