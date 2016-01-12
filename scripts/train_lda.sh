#! /bin/bash

dataset=$1

if [ -z $1 ]; then
	echo "`dataset` required as \$1"
	exit -1
fi

if [ -z $2 ]; then
    echo 'dumping messages'
    python dump_messages_from_interactions.py \
	--interactions_path data/${dataset}/interactions.json \
	--output_path data/${dataset}/content.txt

    echo 'making .mm corpus'
    python lda/corpora.py -m data/${dataset}/content.txt \
	-d data/${dataset}/dict.pkl \
	-i data/${dataset}/id2token.pkl \
	-o data/${dataset}/content.mm
fi

echo 'training model'
time python lda/lda.py --n_topics 50 \
	--n_iters 50 \
	--lda_update_every 1 \
	--lda_chunksize 1000 \
	--id2token data/${dataset}/id2token.pkl \
	--mm_path data/${dataset}/content.mm \
	--model_prefix data/${dataset}/model
