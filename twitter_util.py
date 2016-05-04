import itertools
import pandas as pd
import langdetect
from langdetect import detect

from merge_similar_messages import merge_messages
from datetime import timedelta

def remove_mentions_and_urls(df):
    def aux(r):
        body = r['body'].lower()
        mentions = map(lambda m: '@' + m, r['mentions'])
        for s in itertools.chain(mentions, r['urls']):
            body = body.replace(s.lower(), '')
        return body

    df['body'] = df['body'].map(lambda s: s.lower())
    df['body'] = df[['body', 'mentions', 'urls']].apply(
        aux,
        axis=1
    )
    return df

def detect_lan(msg):
    try:
        return detect(msg)
    except langdetect.lang_detect_exception.LangDetectException:
        return ''

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', required=True)
    parser.add_argument('--hashtag_ban')

    args = parser.parse_args()
    
    try:
        df = pd.read_json('data/{}/interactions.json'.format(args.dataset))
    except (ValueError, IOError):
        df = pd.read_pickle('data/{}/interactions.pkl'.format(args.dataset))
        
    df = df.drop_duplicates(subset=['message_id'])
    df['hashtags'] = df['hashtags'].apply(
        lambda hs: list(set(map(lambda s: s.lower(), hs)))
        )

    if args.hashtag_ban:
        df['hashtags'] = df['hashtags'].apply(
            lambda hs: filter(lambda h: h != args.hashtag_ban, hs)
            )

    df = remove_mentions_and_urls(df)
    df = df[df['body'].map(len) > 10]  # filter short body
    # df = df[df['body'].map(detect_lan) == 'en']  # non english

    # df = merge_messages(df,
    #                     timedelta(days=1),
    #                     50,
    #                     'datetime')

    # df.to_json('data/{}/interactions_new.json'.format(args.dataset),
    #            orient='records')
    df.to_pickle('data/{}/interactions.pkl'.format(args.dataset))

if __name__ == '__main__':
    main()
