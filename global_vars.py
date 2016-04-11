legend_mapping = {
    'lst': 'DP',
    'lst+dij': 'DP+Dij',
    'greedy': 'greedy',
    'random': 'random',
    'quota': 'binary_search'
}

label_mapping = {
    'set_cover_obj': 'Tree size',
    'precision': 'Precision',
    'recall': 'Recall',
    'f1': 'F1',
    'log(running_time)': 'Log(running time)',
    'k_setcover_obj': 'Set cover obj',
    'treesize-objective-median': 'Treesize median'
}

ban_list = set(['adaptive'])

mpl_font = {'weight' : 'normal',
            'size'   : 14}

markers = ['*',  'o', 's', '.', '1']
colors = ['b', 'g', 'r', 'c', 'm']
