#! /bin/bash

if [ -z $1 ];then
    echo '$1 absent'
    exit -1
fi

./scripts/gen_cand_trees.sh \
    $1 \
    50.0 \
    500 \
    "--hours 4 --weight_for_topics 0.4 --weight_for_hashtag_bow 0.4 --weight_for_bow 0.2"