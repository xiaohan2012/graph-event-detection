# coding: utf-8

# Processing thread-like documents
import pandas as pd
import time

from util import get_datetime

KEY_THREAD_ID = 'thread_id'
KEY_DATETIME = 'datetime'
KEY_SENDER_ID = 'sender_id'
KEY_RECIPIENT_IDS = 'recipient_ids'


def add_recipients(df):
    """
    Add recipients information on each thread
    as another column

    Return: pandas.DataFrame
    """
    assert KEY_THREAD_ID in df.columns
    assert KEY_DATETIME in df.columns
    assert KEY_SENDER_ID in df.columns
    all_rows = []
    for k, thread in df.groupby([KEY_THREAD_ID]):
        recipients = set()
        thread = thread.sort_values(KEY_DATETIME)
        for i, r in thread.iterrows():
            if i == 0:
                if thread.shape[0] > 1:
                    rs = [thread.iloc[1][KEY_SENDER_ID]]
                else:
                    rs = []
            else:
                rs = list(recipients)
            new_row = r.tolist() + [rs]
            all_rows.append(new_row)

            recipients.add(r[KEY_SENDER_ID])

    return pd.DataFrame(all_rows,
                        columns=df.columns.tolist() + [KEY_RECIPIENT_IDS])
            

def add_recipients_to_islamic_dataset(path):
    t = pd.read_csv(path, sep='\t',
                    error_bad_lines=False)
    t.rename(columns={
        'ThreadID': KEY_THREAD_ID,
        'MemberID': KEY_SENDER_ID,
        'P_Date': KEY_DATETIME,
        '﻿MessageID': 'message_id',
        'ThreadName': 'subject',
        'Message': 'body',
        'MemberName': 'sender_name',
    },
             inplace=True)
    return add_recipients(t)


def add_timestamp(df, dt_field, ts_field):
    df = df.dropna(subset=[dt_field])
    df[ts_field] = map(lambda dt: time.mktime(
        get_datetime(dt).timetuple()
    ),
                       df[dt_field])
    return df


def collect_user_information(df,
                             id_field='sender_id',
                             other_fields=['sender_name']):
    """
    user id should be the first in `columns`
    """
    columns = [id_field] + other_fields
    return df[columns].drop_duplicates(subset=[id_field])

    
def main():
    input_path = '~/Downloads/IslamicAwakening.txt'
    output_json_path = 'data/islamic/interactions.json'

    df = add_recipients_to_islamic_dataset(input_path)
    df = add_timestamp(df, dt_field="datetime", ts_field="timestamp")
    df.to_json(output_json_path, orient="records")

    user_info = collect_user_information(df,
                                         id_field='sender_id',
                                         other_fields=['sender_name'])
    user_info.rename(columns={'sender_id': 'id'}, inplace=True)
    user_info.to_json('data/islamic/people.json', orient="records")

if __name__ == '__main__':
    main()
