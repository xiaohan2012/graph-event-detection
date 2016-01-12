#! /bin/bash

if [ -z $1 ]; then
    echo 'dumping messages'
    python dump_messages_from_interactions.py \
	--interactions_path data/islamic/interactions.json \
	--output_path data/islamic/content.txt

    echo 'making .mm corpus'
    python lda/corpora.py -m data/islamic/content.txt \
	-d data/islamic/dict.pkl \
	-i data/islamic/id2token.pkl \
	-o data/islamic/content.mm
fi

echo 'training model'
time python lda/lda.py --n_topics 50 \
	--n_iters 50 \
	--lda_update_every 10 \
	--lda_chunksize 1000 \
	--id2token data/islamic/id2token.pkl \
	--mm_path data/islamic/content.mm \
	--model_prefix data/islamic/model
