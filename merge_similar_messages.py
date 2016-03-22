import pandas as pd
from fuzzywuzzy import fuzz

from datetime import timedelta


def merge(df, days=1, time_field='timestamp'):
    return merge_messages(df,
                          timedelta(days=days),
                          50,
                          time_field
                          )

def merge_messages(df, max_time_diff,
                   string_similar_threshold,
                   time_field='timestamp'):
    ret_df = pd.DataFrame(columns=df.columns)
    sender_count = len(df['sender_id'].unique())
    cnt = 0
    msg_processed = 0
    for sender_id, sub_df in df.groupby(['sender_id']):
        msg_processed += len(sub_df)
        if len(sub_df) > 1:
            new_df = merge_messages_by_single_user(
                sub_df,
                max_time_diff,
                string_similar_threshold,
                time_field
                )
            ret_df = ret_df.append(new_df)
            print('{} -> {}'.format(len(sub_df), len(new_df)))
        else:
            ret_df = ret_df.append(sub_df)
        cnt += 1

        print('{} / {}'.format(msg_processed, len(df)))
    return ret_df


def merge_messages_by_single_user(df,
                                  max_time_diff,
                                  string_similar_threshold,
                                  time_field='timestamp'):
    def get_text(r):
        return u'{} {}'.format(
            r.subject, r.body
        )

    merged_msgs = []
    df = df.sort_values(by=[time_field])
    msg_ids = df['message_id'].tolist()
    
    while len(msg_ids) > 0:
        msg_id = msg_ids.pop(0)
        print(msg_id)
        msg = df[df['message_id'] == msg_id].iloc[0]
        msg_text = get_text(msg)

        sub_df = df[df[time_field] > msg[time_field]]
        sub_df = sub_df[
            (sub_df[time_field] - msg[time_field]) <= max_time_diff
        ]
        if not sub_df.empty:
            similar_msgs = sub_df[
                sub_df.apply(
                    lambda r: fuzz.ratio(
                        get_text(r),
                        msg_text),
                    axis=1
                ) > string_similar_threshold
            ]

            for _, m in similar_msgs.iterrows():
                msg['recipient_ids'] += m['recipient_ids']

            similar_msgs_ids = set(similar_msgs['message_id'].tolist())
            msg_ids = [m for m in msg_ids if m not in similar_msgs_ids]
        merged_msgs.append(msg)
    
    return pd.DataFrame(merged_msgs)



def main():
    pass

if __name__ == '__main__':
    main()
