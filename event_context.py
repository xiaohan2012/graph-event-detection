from datetime import datetime
from meta_graph_stat import MetaGraphStat
from interactions import InteractionsUtil as IU


def extract_event_context(interactions, event_tree):
    span = MetaGraphStat(event_tree).time_span()
    start = span['start_time']
    end = span['end_time']
    
    filtered_interactions = []
    for i in interactions:
        assert 'datetime' in i
        dt = i['datetime']
        assert isinstance(dt, datetime)
        if dt >= start and dt <= end:
            filtered_interactions.append(i)
    context_dag = IU.get_meta_graph(filtered_interactions,
                                    decompose_interactions=False,
                                    remove_singleton=True)
    return context_dag
