
def remove_self_talking_events(trees):
    unique_sender_count = lambda t: len(
        set([t.node[n]['sender_id']
             for n in t.nodes_iter()])
    )
    return [t for t in trees if unique_sender_count(t) > 1]


def main():
    import cPickle as pkl

    path = 'tmp/enron/result-greedy--U=2.5--dijkstra=False--timespan=14days----apply_pagerank=False--dist_func=cosine--distance_weights={"topics":0.5,"bow":0.5}--preprune_secs=14days----cand_tree_percent=0.01--root_sampling=out_degree.pkl'
    output_path = 'tmp/enron/result-greedy--U=2.5--dijkstra=False--timespan=14days----apply_pagerank=False--dist_func=cosine--distance_weights={"topics":0.5,"bow":0.5}--preprune_secs=14days----cand_tree_percent=0.01--root_sampling=out_degree-filtered.pkl'

    trees = remove_self_talking_events(pkl.load(open(path)))

    print('{} left'.format(len(trees)))

    pkl.dump(trees, open(output_path, 'w'))

if __name__ == '__main__':
    main()
