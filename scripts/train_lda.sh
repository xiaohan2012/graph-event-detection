#! /bin/bash

dataset=$1

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi

if [ "$2" == "dump_msg" ]; then
    echo 'dumping messages'
    python dump_messages_from_interactions.py \
	--interactions_path data/${dataset}/interactions.* \
	--output_path data/${dataset}/content.txt

    echo 'dumping messages ids'
    python dump_message_ids_from_interactions.py \
	--interactions_path data/${dataset}/interactions.* \
	--output_path data/${dataset}/msg_ids.txt

    echo 'making .mm corpus'
    python lda/corpora.py -m data/${dataset}/content.txt \
	-d data/${dataset}/dict.pkl \
	-i data/${dataset}/id2token.pkl \
	-o data/${dataset}/content.mm \
	$6
fi

if [ -z $3 ] || [ -z $4 ] || [ -z $5 ]; then
    echo '$3 $4 $5 as n_topics, n_iters and ida_chunksize'
    exit -1
fi

echo 'training model'
time python lda/lda.py \
    --n_topics $3 \
    --n_iters $4 \
    --lda_update_every 1 \
    --lda_chunksize $5 \
    --id2token data/${dataset}/id2token.pkl \
    --mm_path data/${dataset}/content.mm \
    --model_prefix data/${dataset}/model \
