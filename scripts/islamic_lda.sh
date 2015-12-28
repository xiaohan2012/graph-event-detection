#! /bin/bash

python lda/corpora.py -m data/islamic/content.txt \
	-d data/islamic/dict.pkl \
	-i data/islamic/id2token.pkl \
	-o data/islamic/content.mm

python lda/lda.py --n_topics 100 \
	--n_iters 50 \
	--lda_update_every 10 \
	--lda_chunksize 1000 \
	--id2token data/islamic/id2token.pkl \
	--mm_path data/islamic/content.mm \
	--model_prefix data/islamic/model
