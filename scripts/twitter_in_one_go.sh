#! /bin/bash

if [ -z $1 ]; then
    echo 'col name empty'
    exit -1
fi

col=$1

./scripts/dump_twitter_stream_data.sh $col

python twitter_util.py -d $col
./scripts/train_lda.sh $col dump_msg 50 150 -1

./scripts/gen_cand_trees.sh \
    $col \
    50.0 \
    500 \
    "--max_time_distance 5-minutes --max_time_span 15-minutes --weight_for_topics 0.4 --weight_for_hashtag_bow 0.4 --weight_for_bow 0.2"

./scripts/make_json_data_for_d3.sh $col
./scripts/make_json_data_for_timeline.sh $col