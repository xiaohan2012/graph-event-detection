import pandas as pd
import networkx as nx
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--json_path')
    parser.add_argument('--meta_graph_path')
    parser.add_argument('--output_path')

    args = parser.parse_args()

    df = pd.read_json(args.json_path)
    g = nx.read_gpickle(args.meta_graph_path)

    node_ids = set([g.node[n]['message_id'] for n in g.nodes_iter()])

    df_p = df[df['message_id'].apply(lambda i: i in node_ids)]

    print("from: ", df.shape)
    print("to: ", df_p.shape)

    df_p.to_json(args.output_path, orient='records')
