from tabulate import tabulate

from meta_graph_stat import MetaGraphStat

def summary(events, tablefmt, summary_kws):
    date_format = '%Y-%m-%d'
    
    table = []
    for i, e in enumerate(events):
        d = MetaGraphStat(e, summary_kws).summary_dict()
        row = ["**#{},**".format(i+1),
               d['basic_structure_stats']['#nodes'],
               "{} {}".format(
                   d['time_span']['start_time'].strftime(date_format),
                   d['time_span']['end_time'].strftime(date_format)
               ),
               # next(s for s in  d['email_content']['subjects(top5)'] if s),  # get first non-empty
               '\n'.join(d['email_content']['subjects(top10)']),
               ' '.join(d['topics']['topic_terms'])
           ]
        table.append(row)
    return tabulate(table, headers=["", "#nodes", "time",
                                    "subject(root)", "terms"],
                    tablefmt=tablefmt)
