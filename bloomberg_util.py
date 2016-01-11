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


def dump2interactions(db, collection_name, output_path):
    valid_articles = []
    for a in db[collection_name].find():
        # filter out articles with single company tag
        if has_multiple_companies(a):
            valid_articles.append(
                transform_article(a)
            )
    json_dump(valid_articles, output_path)


if __name__ == '__main__':
    dump2interactions(MongoClient()['bloomberg'],
                      'articles_test',
                      'data/bloomberg/interactions.json')
