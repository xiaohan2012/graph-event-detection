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

    ('a', 'b', )

if __name__ == '__main__':
    main()
