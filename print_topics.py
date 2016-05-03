import numpy
import re
import gensim

import sys

path = sys.argv[1]

# m = gensim.models.ldamodel.LdaModel.load(path)
m = gensim.models.wrappers.LdaMallet.load(path)


def get_topic_terms(model, topicid, topn, id2token):
    """
    Return a list of `(word_id, probability)` 2-tuples for the most
    probable words in topic `topicid`.
    Only return 2-tuples for the topn most probable words (ignore the rest).
    """
    topic = model.state.get_lambda()[topicid]
    topic = topic / topic.sum()  # normalize to probability distribution
    bestn = numpy.argsort(topic)[::-1][:topn]
    return [id2token[id] for id in bestn]

# for i in xrange(m.num_topics):
#     print(' '.join(get_topic_terms(m, i, 10, m.id2word)))

for i, lst in enumerate(m.show_topics(num_topics=-1, formatted=False)):
    print '{}: {}'.format(i, ' '.join([w for _, w in lst]))

# s = '\n'.join([' '.join([w for _, w in lst])
#                for lst in m.show_topics(num_topics=-1, formatted=False)]
#               )

# print s

