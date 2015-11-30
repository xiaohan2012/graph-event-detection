import numpy
import gensim

m = gensim.models.ldamodel.LdaModel.load('models/model-4-50.lda')


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

for i in xrange(m.num_topics):
    print(' '.join(get_topic_terms(m, i, 20, m.id2word)))
