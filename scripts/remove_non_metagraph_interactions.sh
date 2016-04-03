#! /bin/bash

root_dir='/cs/home/hxiao/code/lst'

dataset=$1
meta_graph_path=$2

if [ -z $1 ]; then
    echo "'dataset' required as \$1"
    exit -1
fi

if [ -z $2 ]; then
    echo "'meta_graph_path' required as \$2"
    exit -1
fi

python remove_non_metagraph_interactions.py \
    --json_path ${root_dir}/data/${dataset}/interactions.json \
    --meta_graph_path ${root_dir}/$2 \
    --output_path ${root_dir}/data/${dataset}/interactions_1.json

mv ${root_dir}/data/${dataset}/interactions.json ${root_dir}/data/${dataset}/interactions_all.json
mv ${root_dir}/data/${dataset}/interactions_1.json ${root_dir}/data/${dataset}/interactions.json