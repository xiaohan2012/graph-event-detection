import numpy as np
import networkx as nx


def main():
    import argparse
    parser = argparse.ArgumentParser('give hint on parameter U')
    parser.add_argument('--meta_graph_path', '-m', required=True)
    parser.add_argument('--percentile', '-p', default=10,
                        type=int, nargs='+')
    args = parser.parse_args()
    
    g = nx.read_gpickle(args.meta_graph_path)
    costs = np.array([g[s][t]['c'] for s, t in g.edges_iter()])
    for p in args.percentile:
        print("At percentile {}: {}".format(
            p, np.percentile(costs, p))
        )
    

if __name__ == '__main__':
    main()
