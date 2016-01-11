import cPickle as pkl

from collections import Counter

from util import load_id2obj_dict
from dag_util import longest_path, get_roots
from events import detect_events


def get_doc(mid, id2interaction):
    return {k: id2interaction[mid][k]
            for k in ('subject', 'body', 'message_id')}


def children_documents(g, root, id2interaction):
    return [get_doc(g.node[s]['message_id'], id2interaction)
            for s in g.successors(root)]


def all_documents(g,  id2interaction):
    return [get_doc(g.node[n]['message_id'], id2interaction)
            for n in g.nodes_iter()]


def longest_path_documents(g, root, id2interaction):
    path = longest_path(g, root)
    return [get_doc(g.node[s]['message_id'], id2interaction)
            for s in path]


def count_message_ids(docs):
    mids = [d['message_id'] for d in docs]
    return Counter(mids)


def main():
    import sys
    from pprint import pprint
    pkl_path = sys.argv[1]

    candidate_events = pkl.load(open(pkl_path))
    g = detect_events(candidate_events, 5)[0]
    mid2interaction = load_id2obj_dict('data/enron.json', 'message_id')
    root = get_roots(g)[0]
    pprint('children documents count: {}'.format(
        count_message_ids(
            children_documents(g, root, mid2interaction))))
    pprint('all documents count: {}'.format(
        count_message_ids(
            all_documents(g, mid2interaction))))
    lpd = longest_path_documents(g, root, mid2interaction)
    pprint('longest path documents count: {}'.format(
        count_message_ids(lpd)))

    pprint('longest path documents\' subject: {}'.format(
        [d['subject'] for d in lpd]
    ))


if __name__ == '__main__':
    main()
