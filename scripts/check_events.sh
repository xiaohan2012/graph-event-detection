#! /bin/bash
dataset=$1
result_path=$2
extra=$3

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi

if [ -z $2 ]; then
	echo "'result_path' required as \$2"
	exit -1
fi

python check_k_best_trees.py \
    --cand_trees_path ${result_path} \
    --interactions_path data/${dataset}/interactions.json \
    --people_path data/${dataset}/people.json \
    --corpus_dict_path data/${dataset}/dict.pkl \
    --lda_model_path  $(ls data/${dataset}/model-*.lda) \
    --people_repr_template "{id}" \
    -k 10 \
	${extra}
