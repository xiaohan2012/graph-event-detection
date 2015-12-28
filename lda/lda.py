import logging
import gensim
import cPickle as pkl
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="LDA training tool")
    parser.add_argument('--n_topics', type=int, required=True,
                        help="number of topics")
    parser.add_argument('--n_iters', type=int, required=True,
                        help="number of iterations to run")
    parser.add_argument('--lda_chunksize', type=int, default=-1,
                        help="chunksize argument to lda training function")
    parser.add_argument('--lda_update_every', type=int, default=1,
                        help="update_every argument to lda training function. if -1, then use all documents")

    parser.add_argument('--id2token_path',  required=True,
                        help="Path to id2token pickle")
    parser.add_argument('--mm_path', required=True,
                        help="Path to messages file(.mm extension)")
    parser.add_argument('--model_prefix', required=True,
                        help="""Prefix of path to output model.
#topics and #iters will be appended""")

    arg = parser.parse_args()

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    # load id->word mapping (the dictionary),
    # one of the results of step 2 above
    id2word = pkl.load(open(arg.id2token_path))
    print(len(id2word))

    # load corpus iterator
    mm = gensim.corpora.MmCorpus(arg.mm_path)

    print(mm)

    lda = gensim.models.ldamodel.LdaModel(corpus=mm,
                                          id2word=id2word,
                                          num_topics=arg.n_topics,
                                          update_every=arg.lda_update_every,
                                          chunksize= (mm.num_docs
                                                      if arg.lda_chunksize == -1 
                                                      else arg.lda_chunksize),
                                          passes=arg.n_iters)

    lda.print_topics(arg.n_topics, 20)
    lda.save("{}-{}-{}.lda".format(
        arg.model_prefix,
        arg.n_topics, arg.n_iters
    ))


if __name__ == '__main__':
    main()
