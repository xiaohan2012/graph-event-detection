import itertools


def remove_entities(df):
    def aux(r):
        body = r['body']
        mentions = map(lambda m: '@' + m, r['mentions'])
        hashtags = map(lambda h: '#' + h, r['hashtags'])

        for s in itertools.chain(mentions, hashtags, r['urls']):
            body = body.replace(s, '')
        return body

    new_body = df[['body', 'mentions', 'hashtags', 'urls']].apply(
        aux,
        axis=1
    )

    df['body'] = new_body

    return df
