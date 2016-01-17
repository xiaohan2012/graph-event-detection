#! /bin/bash

dataset=$1

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi


extra=$2


methods=("greedy" "random" "lst --dij")
weeks=(2)
# Us=(1 2 5)
# cand_n_percents=(0.1 0.2 0.3 0.4)
Us=(5)
cand_n_percents=(0.1 0.2)


for cand_n_percent in "${cand_n_percents[@]}"
do
    for U in "${Us[@]}"
    do
	for week in "${weeks[@]}"
	do
	    for method in "${methods[@]}"
	    do
		time python gen_candidate_trees.py \
		    --method=${method} \
		    --root_sampling=out_degree \
		    --weeks=${week} \
		    --dist=euclidean \
		    --result_prefix=tmp/${dataset}/result- \
		    --lda_path=$(ls data/${dataset}/model-*.lda) \
		    --corpus_dict_path=data/${dataset}/dict.pkl \
		    --interaction_path=data/${dataset}/interactions.json \
		    --meta_graph_path_prefix=tmp/${dataset}/meta-graph \
		    --U=${U} \
		    --cand_n_percent=${cand_n_percent} \
		    ${extra}
	    done
	done
    done
done