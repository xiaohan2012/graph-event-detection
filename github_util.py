import pandas as pd
from util import json_load
from thread_util import KEY_THREAD_ID, \
    KEY_TIMESTAMP, \
    KEY_SENDER_ID, \
    KEY_RECIPIENT_IDS, \
    add_recipients, \
    collect_user_information, \
    drop_thread_with_no_comments, \
    fillna_subject_and_body


def make_label_string(labels):
    return ' '.join(map(lambda l: 'L({})'.format(l), labels))


def make_dataframe(path):
    threads = json_load(path)
    all_messages = []
    for i, th in enumerate(threads):
        h = th['head']

        if len(th['tail']) == 0:
            continue

        all_messages.append(
            (h['id'],
             i, h['title'],
             (h['body'] or '') + ' ' + make_label_string(h['labels']),
             h['sender'], h['created_at'])
        )
        for t in th['tail']:
            all_messages.append(
                (t['id'], i,
                 '', t['body'],
                 t['sender'], t['created_at'])
            )
    return pd.DataFrame(all_messages,
                        columns=['id',
                                 KEY_THREAD_ID, 'subject', 'body',
                                 KEY_SENDER_ID, KEY_TIMESTAMP])
        

def dump2interactions(input_path, output_path):
    df = make_dataframe(input_path)

    df = add_recipients(df)

    print('before drop empty thread: ', df.shape)
    df = drop_thread_with_no_comments(df)
    print('after drop empty thread: ', df.shape)

    print('fillna subject/body before: ', df['body'].dropna().shape)
    df = fillna_subject_and_body(df)
    print('fillna subject/body after: ', df['body'].dropna().shape)

    df.to_json(output_path, orient="records")


def dump2people(input_path, output_path):
    df = make_dataframe(input_path)
    user_info = collect_user_information(
        df,
        id_field='sender_id',
        other_fields=[]
    )
    user_info.rename(columns={'sender_id': 'id'}, inplace=True)
    user_info.to_json(output_path, orient="records")

if __name__ == '__main__':
    dump2interactions('data/sklearn/raw.json',
                      'data/sklearn/interactions.json')
    dump2people('data/sklearn/raw.json',
                'data/sklearn/people.json')






