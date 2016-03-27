#! /bin/bash

export root_dir='/cs/home/hxiao/code/lst'
export dir_suffix="-budget-experiment"

PARALLEL="/cs/home/hxiao/.local/bin/parallel --tmpdir /cs/home/hxiao/tmp "

if [ -z $1 ]; then
    echo "'dataset' required as \$1"
    exit -1
fi

if [ -z $2 ]; then
    echo "'operation' required as \$2"
    exit -1
fi

operation=$2

export dataset=$1

echo "using dataset '${dataset}'"


#  "quota"
# "lst --dij"


if [ ${operation} == 'gen' ]; then

    U_start=0.0
    U_step=2.5
    U_end=50.0

    # U_start=1.0
    # U_step=1.0
    # U_end=2.0

    Us=$(seq ${U_start} ${U_step} ${U_end})

    methods=("random" "greedy" "lst+dij" "quota")
    # methods=("quota")

    if [ ! -d ${root_dir}/tmp/${dataset}${dir_suffix} ]; then
	mkdir -p ${root_dir}/tmp/${dataset}${dir_suffix}
    else
	rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/result-*
	rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/paths-*
    fi

    function run_experiment {
	if [ -z $1 ]; then
	    echo 'U should be given'
	    exit -1
	fi

	if [ -z $2 ]; then
	    echo 'method should be given'
	    exit -1
	fi

	if [ -z $3 ]; then
	    echo 'cand_n should be given'
	    exit -1
	fi

	python gen_candidate_trees.py \
	    --method=$2 \
	    --root_sampling=upperbound \
	    --dist=cosine \
	    --result_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/result- \
            --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/paths- \
	    --lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	    --corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	    --interaction_path=${root_dir}/data/${dataset}/interactions.json \
	    --meta_graph_path_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/meta-graph \
	    --U=$1 \
            --cand_n=$3 \
            --random_seed 123456 \
	    --weight_for_topics=0.8 \
	    --weight_for_bow=0.2 \
	    --weeks 4
	    # --days=1 \
	    # --weight_for_topics=0.4 \
	    # --weight_for_hashtag_bow=0.4 \
	    # --weight_for_bow=0.2

    }


    export -f run_experiment

    echo "generating the meta graph..."
    run_experiment 0 random 1 # gen the metagraph

    # rm the result
    rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/result-*
    rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/paths-*

    # 60 comes from sampling method experiment result
    ${PARALLEL} run_experiment ::: ${Us[@]}  :::  ${methods[@]} ::: 40
fi

if [ ${operation} == 'eval' ]; then
    python budget_evaluation.py \
	-e "${root_dir}/tmp/${dataset}${dir_suffix}/result-*" \
	-k 10 \
	-o "${root_dir}/tmp/${dataset}${dir_suffix}/eval_result.pkl"
fi

if [ ${operation} == 'viz' ]; then
    output_dir="${root_dir}/tmp/${dataset}${dir_suffix}/fig"
    if [ ! -d ${output_dir} ]; then
	mkdir -p ${output_dir}
    fi
    python draw_evaluation_result.py \
	--result_path "${root_dir}/tmp/${dataset}${dir_suffix}/eval_result.pkl" \
	--xlabel U \
	--output_dir ${output_dir}
    ssh shell.cs.helsinki.fi mkdir /cs/home/hxiao/public_html/figures/${dataset}${dir_suffix}
    scp  ${output_dir}/*  shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/${dataset}${dir_suffix}
fi