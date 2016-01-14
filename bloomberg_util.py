from pymongo import MongoClient
from util import json_dump

TAG_PREFIX = 'topics/companies/'


def get_companies(article):
    return [t.split('/')[-1]
            for t in article['tags']
            if t.startswith(TAG_PREFIX)]


def has_multiple_companies(article):
    companies = get_companies(article)
    return len(companies) > 1


def transform_article(a):
    """some rename of fields
    """
    return {
        'message_id': a['url'],
        'subject': a['title'],
        'body': ' '.join(a['body']),
        'timestamp': a['publish_time'],
        'participant_ids': get_companies(a)
    }


def articles_articles(db, collection_name):
    valid_articles = []
    for a in db[collection_name].find():
        # filter out articles with single company tag
        if has_multiple_companies(a):
            valid_articles.append(
                transform_article(a)
            )
    return valid_articles


def dump2interactions(db, collection_name, output_path):
    articles = articles_articles(db, collection_name)
    print('# valid articles: ', len(articles))
    json_dump(articles, output_path)
    return articles


def collect_people_info(articles):
    participant_ids = set(
        itertools.chain(*[a['participant_ids'] for a in articles])
        )
    return [{'id': p} for p in participant_ids]


if __name__ == '__main__':
    articles = dump2interactions(MongoClient()['bloomberg'],
                                 'articles',
                                 'data/bloomberg/interactions.json')

    json_dump(collect_people_info(articles),
              'data/bloomberg/people.json')
