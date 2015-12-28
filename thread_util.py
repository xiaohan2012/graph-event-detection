# Processing thread-like documents
import pandas as pd

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
        thread = thread.sort(KEY_DATETIME)
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

    print(df)
    print(all_rows)
    return pd.DataFrame(all_rows,
                        columns=df.columns.tolist() + [KEY_RECIPIENT_IDS])
            
