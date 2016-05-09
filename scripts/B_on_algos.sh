#! /bin/bash

DEBUG=false

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

if [ ${operation} == 'gen' ]; then
    if [ ${DEBUG} = true ]; then
	U_start=0.0
	U_step=5.0
	U_end=10.0
    else
	U_start=5.0
	U_step=5.0
	U_end=100.0
    fi

    Us=$(seq ${U_start} ${U_step} ${U_end})

    methods=("random" "greedy" "lst" "lst+dij" "quota")

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

	if [ ${dataset} == "letter" ]; then
	    extra="--max_time_distance 90-days --max_time_span 365-days --weight_for_topics=1.0 --weight_for_bow=0.0"
	elif [ ${dataset} != "enron_small" ]; then
	    extra="--days=1   --weight_for_topics=0.4  --weight_for_hashtag_bow=0.4   --weight_for_bow=0.2"
	else
	    extra="--weight_for_topics=0.8 --weight_for_bow=0.2 --weeks 4"
	fi
	echo ${extra}

	python gen_candidate_trees.py \
	    --method=$2 \
	    --root_sampling=upperbound \
	    --dist=cosine \
	    --msg_ids_path ${root_dir}/data/${dataset}/msg_ids.txt \
	    --result_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/result- \
            --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/paths- \
	    --lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	    --corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	    --interaction_path ${root_dir}/data/${dataset}/interactions.* \
	    --meta_graph_path_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/meta-graph \
	    --U=$1 \
            --cand_n=$3 \
            --random_seed 123456 \
	    ${extra}

    }


    export -f run_experiment

    echo "generating the meta graph..."
    run_experiment 0 random 1 # gen the metagraph

    # rm the result
    rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/result-*
    rm -r ${root_dir}/tmp/${dataset}${dir_suffix}/paths-*

    # 60 comes from sampling method experiment result
    ${PARALLEL} run_experiment ::: ${Us[@]}  :::  ${methods[@]} ::: 100
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