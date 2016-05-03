import pandas as pd
from meta_graph import convert_to_meta_graph
from interactions import InteractionsUtil


def main():
    K, M, C, H = 'K', 'M', 'C', 'H'
    interactions = [
        {'sender_id': K, 'recipient_ids': (M, C), 'datetime': 1, 'message_id': 'K->(M, C): code(1)'},
        {'sender_id': M, 'recipient_ids': [K], 'datetime': 3, 'message_id': 'M->K: read(3)'},
        {'sender_id': K, 'recipient_ids': [M], 'datetime': 4, 'message_id': 'K->M: read(3)'},
        {'sender_id': C, 'recipient_ids': [H], 'datetime': 2, 'message_id': 'C->H: eat(2)'},
        {'sender_id': H, 'recipient_ids': [C], 'datetime': 3, 'message_id': 'H->C: eat(2)'},
    ]
    InteractionsUtil.decompose_interactions(interactions)
    node_names, sources, targets, time_stamps = InteractionsUtil.unzip_interactions(
        InteractionsUtil.decompose_interactions(interactions)
    )
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)

    print graph.edges()


def main1():
    C, P, T1, T2 = ('CEO', 'PM', 'T1', 'T2')
    p = 'progress'
    s = 'suggetion'
    f = 'football'
    correct_edge_to_color = {
        ('a', 'b'): 'red',
        ('b', 'c'): 'red',
        ('c', 'd'): 'red',
        ('e', 'f'): 'green'
    }

    interactions = [
        ('a', C, [P], p, 1),
        ('b', P, [T1, T2], p, 2),
        ('c', T1, [P], p, 3),
        ('d', P, [C], p, 4),
        ('e', T2, [P], s, 3),
        ('f', P, [C], p, 5),
        ('g', T2, [T1], f, 4)
    ]
    new_interactions = []
    for msg_id, sender, recs, topic, time in interactions:
        new_interactions.append(
            {'sender_id': sender,
             'recipient_ids': recs,
             'datetime': time,
             'message_id': msg_id},
        )
    
    node_names, sources, targets, time_stamps = InteractionsUtil.unzip_interactions(
        new_interactions
    )
    graph = convert_to_meta_graph(node_names, sources, targets, time_stamps)
    # nx.write_dot(graph, 'tmp/illustration.dot')
    print """digraph {
    node [fontsize=20];
"""
    for u, v in  graph.edges():
        print "{} -> {}[color={}];".format(
            u, v,
            # correct_edge_to_color.get((u, v), 'gray')
            'black'
        )
    print "}"
    
    df = pd.DataFrame(new_interactions,
                      columns=['sender_id', 'recipient_ids', 'datetime'],
                      index=[i[0] for i in interactions])
    df = df.rename(columns={'sender_id': 'sender',
                       'recipient_ids': 'recipients',
                       'datetime': 'time'})

    mapping = {
        1: 'Mon',
        2: 'Tue',
        3: 'Wed',
        4: 'Thu',
        5: 'Fri'
    }
    df['time'] = df['time'].map(lambda t: mapping[t])
    df.to_latex('tmp/example.tex')

if __name__ == '__main__':
    main1()
