import itertools
import pandas as pd


def remove_entities(df):
    def aux(r):
        body = r['body']
        mentions = map(lambda m: '@' + m, r['mentions'])
        hashtags = map(lambda h: '#' + h, r['hashtags'])

        for s in itertools.chain(mentions, hashtags, r['urls']):
            body = body.replace(s.lower(), '')
        return body

    df['body'] = df['body'].map(lambda s: s.lower())
    df['body'] = df[['body', 'mentions', 'hashtags', 'urls']].apply(
        aux,
        axis=1
    )

    return df


def main():
    df = pd.read_json('data/twitter/interactions.json')
    df = remove_entities(df)
    df = df[df['body'].map(len) > 10]  # filter short body
    df.to_json('data/twitter/interactions.json',
               orient='records')

if __name__ == '__main__':
    main()
