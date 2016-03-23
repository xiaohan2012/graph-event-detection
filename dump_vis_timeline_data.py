from check_k_best_trees import k_best_trees
from meta_graph_stat import MetaGraphStat, build_default_summary_kws_from_path
from datetime import datetime
from collections import Counter


def format_time(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:00:00')


def run(cand_trees, k, summary_kws, undirected):
    interactions = summary_kws['topics']['interactions']
    mid2i = {
        i['message_id']: i
        for i in interactions
    }
    trees = k_best_trees(cand_trees, k)
    summaries = [MetaGraphStat(t, summary_kws).summary_dict() for t in trees]

    items = []
    groups = []
    start_times = []
    end_times = []
    added_id_count = Counter()
    counter = 0
    for group_id, (summ, t) in enumerate(zip(summaries, trees)):
        group_id += 1
        for i in t.nodes_iter():
            counter += 1
            items.append({
                'id': counter,
                'content': (mid2i[i]['subject'].strip()
                            if mid2i[i]['subject'] else
                            mid2i[i]['body']),
                'start': format_time(mid2i[i]['datetime']),
                'group': group_id
            })
            added_id_count[i] += 1
        counter += 1
        items.append(
            {
                'id': counter,
                # 'id': 'event_{}'.format(group_id),
                'start': format_time(summ['time_span']['start_time']),
                'end': format_time(summ['time_span']['end_time']),
                'content': 'Event {}'.format(group_id),
                'group': group_id,
                'type': 'background'
            })
        g = {
            'id': group_id,
            'terms': summ['topics']['topic_terms'],
            'participants': dict(
                summ['participants']['participant_count']
            ),
            'start': format_time(summ['time_span']['start_time']),
            'end': format_time(summ['time_span']['end_time']),
            'days': (summ['time_span']['end_time'] - summ['time_span']['start_time']).days,
            'link_type_freq': summ['link_type_freq']
        }
        if 'hashtags' in summ:
            g['hashtags'] = summ['hashtags']
        groups.append(g)

        start_times.append(summ['time_span']['start_time'])
        end_times.append(summ['time_span']['end_time'])

    return {
        'items': items,
        'groups': groups,
        'start': format_time(min(start_times)),
        'end': format_time(max(end_times))
    }


def main():
    import argparse
    import cPickle as pkl
    from util import json_dump

    parser = argparse.ArgumentParser('dump vis timeline data')
    parser.add_argument('--cand_trees_path', required=True)
    parser.add_argument('--output_path', required=True)
    parser.add_argument('--interactions_path', required=True)
    parser.add_argument('--people_path', required=True)
    parser.add_argument('--corpus_dict_path', required=True)
    parser.add_argument('--lda_model_path', required=True)
    parser.add_argument('--people_repr_template', type=str,
                        default="{id}")
    parser.add_argument('-k', type=int, default=10)
    parser.add_argument('--undirected', default=False, action="store_true")

    args = parser.parse_args()
    
    summary_kws = build_default_summary_kws_from_path(
        args.interactions_path,
        args.people_path,
        args.corpus_dict_path,
        args.lda_model_path,
        args.people_repr_template,
        undirected=args.undirected
    )
    trees = pkl.load(open(args.cand_trees_path))
    
    # add hashtags if there
    print(len(trees))
    first_node = trees[0].nodes()[0]
    if 'hashtags' in trees[0].node[first_node]:
        print('add hashtags')
        summary_kws['hashtags'] = {}

    data = run(trees,
               args.k,
               summary_kws,
               args.undirected)
    json_dump(data, args.output_path)
    

if __name__ == '__main__':
    main()
