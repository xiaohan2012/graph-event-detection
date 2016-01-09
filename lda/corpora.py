import re
import codecs
import nltk
import logging

from nltk.stem.porter import PorterStemmer

from gensim import corpora

logging.basicConfig()

logger = logging.getLogger('CorpusEnron')
logger.setLevel(logging.DEBUG)

stemmer = PorterStemmer()


def load_items_by_line(path):
    with codecs.open(path, 'r', 'utf8') as f:
        items = set([l.strip()
                    for l in f])
    return items


class CorpusEnron(corpora.TextCorpus):
    stoplist = load_items_by_line('lemur-stopwords.txt')
    # valid_token_regexp = re.compile('^[a-z]+$')
    valid_token_regexp = re.compile('^[a-zA-Z][a-zA-Z0-9]?[_()\-a-zA-Z0-9]+$')
    MIN_WORD_LEN = 2

    MAX_WORD_LEN = 15

    def get_texts(self):
        """
        Parse documents from the .cor file provided in the constructor. Lowercase
        each document and ignore some stopwords.

        .cor format: one document per line, words separated by whitespace.
        """
        with codecs.open(self.input) as f:
            for i, doc in enumerate(f):
                if (i+1) % 1000 == 0:
                    logger.debug('{} lines processed'.format(i+1))
                yield [
                    word for word in nltk.word_tokenize(doc.lower())
                    if (word not in CorpusEnron.stoplist and
                        CorpusEnron.valid_token_regexp.match(word) and
                        len(word) > CorpusEnron.MIN_WORD_LEN and
                        len(word) < CorpusEnron.MAX_WORD_LEN)
                ]

    def __len__(self):
        """Define this so we can use `len(corpus)`"""
        if 'length' not in self.__dict__:
            logger.info("caching corpus size (calculating number of documents)")
            self.length = sum(1 for doc in self.get_texts())
        return self.length


if __name__ == "__main__":
    from argparse import ArgumentParser
    import cPickle as pkl
    
    parser = ArgumentParser(
        description="Corpus preprocessing in order to input to LDA tool"
    )
    parser.add_argument('--messages_path', '-m', required=True,
                        help="Path to messages file(.txt extension)")
    parser.add_argument('--dict_path', '-d', required=True,
                        help="Path to dictionary pickle")
    parser.add_argument('--id2token_path', '-i', required=True,
                        help="Path to id2token pickle")
    parser.add_argument('--mm_output_path', '-o', required=True,
                        help="Path to output file in .mm")

    logger.info('start')
    arg = parser.parse_args()
    c = CorpusEnron(arg.messages_path)
    
    logger.info('building dict')
    dictionary = corpora.Dictionary(c.get_texts())

    logger.info('filtering dict')
    print(dictionary)
    dictionary.filter_extremes(no_below=2)
    print(dictionary)

    logger.info('saving dict')
    dictionary.save(arg.dict_path)
    
    logger.info('dumping .mm')
    vectors = [dictionary.doc2bow(tokens) for tokens in c.get_texts()]
    corpora.MmCorpus.serialize(arg.mm_output_path, vectors)
    
    logger.info('saving id2token')
    id2token = {i: t
                for t, i in dictionary.token2id.items()}
    print(len(id2token))
    pkl.dump(id2token, open(arg.id2token_path, 'w'))

    # corpora.MmCorpus.save_corpus('messages.mm', c)

    # id2token = {i: t
    #             for t, i in c.dictionary.token2id.items()}
    # import cPickle as pkl
    # pkl.dump(id2token, open('id2token.pkl', 'w'))
