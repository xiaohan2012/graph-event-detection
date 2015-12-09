import os
import gensim
from tabulate import tabulate

from meta_graph_stat import MetaGraphStat
from util import load_json_by_line


def summary(events, tablefmt):
    CURDIR = os.path.dirname(os.path.abspath(__file__))

    interactions = load_json_by_line('data/enron.json')
    people_info = load_json_by_line('data/people.json')

    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, 'models/dictionary.pkl')
    )

    lda = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, 'models/model-4-50.lda')
    )

    STAT_KWS = {
        'temporal_traffic': False,
        'topics': {
            'interactions': interactions,
            'dictionary': dictionary,
            'lda': lda,
            'top_k': 10
        },
        'email_content': {
            'interactions': interactions,
            'top_k': 5
        },
        'participants': False
    }
    date_format = '%Y-%m-%d'
    
    table = []
    for i, e in enumerate(events):
        d = MetaGraphStat(e, STAT_KWS).summary_dict()
        row = ["**#{},**".format(i+1),
               d['basic_structure_stats']['#nodes'],
               "{} {}".format(
                   d['time_span']['start_time'].strftime(date_format),
                   d['time_span']['end_time'].strftime(date_format)
               ),
               next(s for s in  d['email_content']['subjects(top5)'] if s),  # get first non-empty
               ' '.join(d['topics']['topic_terms'])
           ]
        table.append(row)
    return tabulate(table, headers=["", "#nodes", "time",
                                    "subject(root)", "terms"],
                    tablefmt=tablefmt)
