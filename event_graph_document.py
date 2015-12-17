
import cPickle as pkl

from util import load_msgid2interaction_dict
from dag_util import longest_path, get_roots
from events import detect_events


def get_doc(mid, id2interaction):
    return {k: id2interaction[mid][k]
            for k in ('subject', 'body', 'message_id')}


def children_documents(g, root, id2interaction):
    return [get_doc(g.node[s]['message_id'], id2interaction)
            for s in g.successors(root)]


def longest_path_documents(g, root, id2interaction):
    path = longest_path(g, root)
    return [get_doc(g.node[s]['message_id'], id2interaction)
            for s in path]


def main():
    import sys
    from pprint import pprint
    from collections import Counter
    pkl_path = sys.argv[1]

    candidate_events = pkl.load(open(pkl_path))
    g = detect_events(candidate_events, 5)[0]
    mid2interaction = load_msgid2interaction_dict('data/enron.json')
    root = get_roots(g)[0]
    docs = children_documents(g, root, mid2interaction)
    mids = [d['message_id'] for d in docs]
    pprint(Counter(mids))

if __name__ == '__main__':
    main()
