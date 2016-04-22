import pymongo
import ujson as json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime as dt


consumer_key = "cadDGYYIDjUz2aCzBqcy1Ff99"
consumer_secret = "Xi02ZDEvmWKMVw20WKoRmnUJlkiem3SbKeCRRuCfo8Oop8KF4n"
access_token = "363711223-HEyPCS2ediosYWHLsE0IFy9kWgHyjDLLIFY4L76T"
access_token_secret = "yRuW7kuRLmro52lVU3XnEW4bynWRij3eXUD4Np5ZozhoI"

# access_token = "ENTER YOUR ACCESS TOKEN"
# access_token_secret = "ENTER YOUR ACCESS TOKEN SECRET"
# consumer_key = "ENTER YOUR API KEY"
# consumer_secret = "ENTER YOUR API SECRET"

DB = 'twitter_stream'


def convert_tweet(d):
    mentions = d["entities"]['user_mentions']
    return {
        'message_id': d['id'],
        'subject': '',
        'body': d['text'],
        'sender_id': d['user']['id'],
        'recipient_ids': [m['id'] for m in mentions],
        'datetime': dt.fromtimestamp(float(d['timestamp_ms']) / 1000),
        'mentions': [m['screen_name'] for m in mentions],
        "hashtags": [h['text'] for h in d['entities']["hashtags"]],
        'urls': [u['url'] for u in d['entities']["urls"]]
    }


class StdOutListener(StreamListener):
    def __init__(self, mongo_col):
        self.collection = pymongo.MongoClient()[DB][mongo_col]
        self.collection.remove()

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        if data.get("lang") == 'en':
            if data.get("entities") and \
               data.get("entities").get('user_mentions') and \
               data["entities"]['user_mentions']:
                tweet = convert_tweet(data)
                # print tweet
                self.collection.insert(tweet)
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('')
    
    parser.add_argument('--terms', nargs='+')
    parser.add_argument('--mongo_col')
    
    args = parser.parse_args()

    l = StdOutListener(args.mongo_col)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    stream.filter(track=args.terms)
