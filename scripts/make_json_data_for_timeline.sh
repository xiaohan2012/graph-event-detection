if [ -z $1 ]; then
	echo "dataset name is not given"
	exit -1
fi

dataset=$1
pickle_dir="tmp/${dataset}"
extra=$2

output_dir="/cs/home/hxiao/public_html/event_html/data/${dataset}"

if [ ! -d "${output_dir}/timeline" ]; then
	mkdir -p "${output_dir}/timeline"
fi

for p in $(ls ${pickle_dir}/result-*.pkl); do
	echo "${p}"
	output_name=$(basename ${p})
	output_name="${output_name%.*}.json"

	python dump_vis_timeline_data.py \
		--cand_trees_path ${p} \
		--interactions_path data/${dataset}/interactions.json \
		--people_path data/${dataset}/people.json \
		--corpus_dict_path  data/${dataset}/dict.pkl \
		--lda_model_path $(ls data/${dataset}/model-*.lda) \
		--output_path "${output_dir}/timeline/${output_name}" \
		-k 10 \
		${extra}
	echo "Writing to '${output_dir}/timeline/${output_name}'"
done

echo "dumping timeline names..."
python dump_all_event_json_names.py \
	${output_dir}/timeline \
	${output_dir}/timeline_names.json

chmod -R a+rx /cs/home/hxiao/public_html/event_html/data
