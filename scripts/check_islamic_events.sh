#! /bin/bash
if [ -z $1 ]; then
    echo 'candidate events result path is not there'
    exit -1
fi

python check_k_best_trees.py \
$1 \
data/islamic/interactions.json \
data/islamic/people.json \
data/islamic/dict.pkl \
data/islamic/model-100-50.lda