import pandas as pd
from fuzzywuzzy import fuzz


def merge_messages(df, max_time_diff,
                   string_similar_threshold,
                   time_field='timestamp'):
    ret_df = pd.DataFrame(columns=df.columns)
    for _, sub_df in df.groupby(['sender_id']):
        ret_df = ret_df.append(merge_messages_by_single_user(
            sub_df,
            max_time_diff,
            string_similar_threshold,
            time_field)
        )
    return ret_df


def merge_messages_by_single_user(df,
                                  max_time_diff,
                                  string_similar_threshold,
                                  time_field='timestamp'):
    def get_text(r):
        return u'{} {}'.format(
            r.subject, r.body
        )

    df_after_merging = pd.DataFrame(columns=df.columns)
    
    df = df.sort_values(by=[time_field])
    msg_ids = df['message_id'].tolist()

    while len(msg_ids) > 0:
        msg_id = msg_ids.pop(0)
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
                        r.subject,
                        msg.subject),
                    axis=1
                ) > string_similar_threshold
            ]
            if not similar_msgs.empty:
                similar_msgs = similar_msgs[
                    similar_msgs.apply(
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

        df_after_merging = df_after_merging.append(msg)

    return df_after_merging


def main():
    pass

if __name__ == '__main__':
    main()
