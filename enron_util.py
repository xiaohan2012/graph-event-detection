import pandas as pd
import re
from pandas import DataFrame
from datetime import datetime, timedelta
from merge_similar_messages import merge_messages
from util import load_json_by_line, json_load, json_dump


def clean_interaction_data(input_path, output_path):
    obj = load_json_by_line(input_path)
    df = DataFrame(obj)
    df['timestamp'] = df['datetime']
    df['datetime'] = df['timestamp'].map(
        lambda ts: str(datetime.fromtimestamp(ts))
        )
    df.to_json(output_path, orient="records")


def convert_interaction_user_id_to_string(df):
    df['sender_id'] = df['sender_id'].map(str)
    df['recipient_ids'] = df['recipient_ids'].map(
        lambda ids: map(str, ids)
        )
    return df


def convert_people_user_id_to_string(df):
    df['id'] = df['id'].map(str)
    return df

reg_exps = [re.compile(r'-{2,}\s*' + s)
            for s in ('original message',
                      'forwarded')
            ]
reg_exps.append(
    re.compile('*************************'.replace('*', '\\*'))
    )

email = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+'
datetime = '\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}(:\d{2})?\s*[aApP][mM]'
reg_exps.append(
    re.compile('<?{}>?.*{}'.format(email,
                               datetime))
)
reg_exps.append(
    re.compile('{}.*[Tt][Oo].*<?{}>?'.format(datetime,
                                         email))
)


def truncate_message(text):
    text_lower = text.lower()
    for reg in reg_exps:
        for m in reg.finditer(text_lower):
            return text[:m.start()]
    return text


def process_message_body(df):
    df['body'] = df['body'].map(truncate_message)
    df['body'] = df['body'].map(lambda b: b.replace('=20', ''))
    return df

def filter_and_save(df):
    # df = process_message_body(df)
    # df = df[df['body'].map(len) > 10]  # filter short body
    
    # potential: 14557
    black_list = [256, 1175]
    for s in black_list:
        df = df[df['sender_id'] != s]

    df.to_json('data/enron/interactions.json',
               orient="records")

if __name__ == '__main__':
    df = pd.read_json('data/enron/interactions.json')
    df = merge_messages(
        df, 
        timedelta(weeks=2),
        50,
        'timestamp'
        )
    df.to_json('data/enron/interactions.json')
    # frequent_senders = df['sender_id'].value_counts().index[20:40]
    # for s in frequent_senders:
    #     print(s)
    #     print(df[df['sender_id'] == s]['subject'][:10])
    #     print('*' * 20)
    
    # filter_and_save(df)
