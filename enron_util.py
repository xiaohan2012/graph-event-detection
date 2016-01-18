import pandas as pd
from pandas import DataFrame
from datetime import datetime
from util import load_json_by_line, json_load, json_dump


def clean_interaction_data(input_path, output_path):
    obj = load_json_by_line(input_path)
    df = DataFrame(obj)
    df['timestamp'] = df['datetime']
    df['datetime'] = df['timestamp'].map(
        lambda ts: str(datetime.fromtimestamp(ts))
        )
    df.to_json(output_path, orient="records")

def convert_interaction_user_id_to_string(input_path, output_path):
    df = pd.read_json(input_path)
    df['sender_id'] = df['sender_id'].map(str)
    df['recipient_ids'] = df['recipient_ids'].map(
        lambda ids: map(str, ids)
        )
    df.to_json(output_path, orient="records")

def convert_people_user_id_to_string(input_path, output_path):
    df = pd.read_json(input_path)
    df['id'] = df['id'].map(str)
    df.to_json(output_path, orient="records")

if __name__ == '__main__':
    clean_interaction_data('data/enron/interactions.json',
                           'data/enron/interactions.json')
    convert_interaction_user_id_to_string(
        'data/enron/interactions.json',
        'data/enron/interactions.json'
        )
    
    convert_people_user_id_to_string(
        'data/enron/people.json',
        'data/enron/people.json'
        )
