import os
import gensim
import ujson as json
import glob

CURDIR = os.path.dirname(os.path.abspath(__file__))

def load_meta_graph_necessities():
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, 'test/data/test.lda')
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
    )
    interactions = json.load(
        open(os.path.join(CURDIR,
                          'test/data/enron_test.json')))
    return lda_model, dictionary, interactions


def remove_tmp_data(directory):
    # remove the pickles
    files = glob.glob(os.path.join(CURDIR,
                                   "{}/*".format(directory)))
    for f in files:
        os.remove(f)
