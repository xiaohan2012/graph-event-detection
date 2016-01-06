from pandas import DataFrame
from datetime import datetime
from util import load_json_by_line


def clean_interaction_data(input_path, output_path):
    obj = load_json_by_line(input_path)
    df = DataFrame(obj)
    df['timestamp'] = df['datetime']
    df['datetime'] = map(lambda ts: str(datetime.fromtimestamp(ts)),
                         df['timestamp'])
    df.to_json(output_path, orient="records")

if __name__ == '__main__':
    clean_interaction_data('data/enron/interactions.json',
                           'data/enron/interactions_new.json')
