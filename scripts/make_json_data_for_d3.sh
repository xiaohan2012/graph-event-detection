# Generate the json data for top events
# 4 types of data for each candidate tree
# - event with context
#   - meta-graph
#   - original graph
# - event without context
#   - meta-graph
#   - original graph

# Note:
# - original graph is not allowed for undirected case

if [ -z $1 ]; then
	echo "dataset name is not given"
	exit -1
fi


dataset=$1
pickle_dir=tmp/${dataset}
extra=$2

output_dir="/cs/home/hxiao/public_html/event_html/data/${dataset}"
metadata_dir="/cs/home/hxiao/public_html/event_html/data/${dataset}"

if [ ! -d $output_dir ]; then
	mkdir -p ${output_dir}
fi

for p in $(ls ${pickle_dir}/result-*.pkl); do
	echo "${p}"
	# just events
	output_name=$(basename ${p})
	output_name="${output_name%.*}.json"

	if [ ! -f "${output_dir}/event/original_graph/${output_name}" ]; then
		echo 'dumping event to original graph'
		python dump_events_to_json.py \
			--candidate_tree_path ${p} \
			--dirname "${output_dir}/event/original_graph" \
			--interactions_path "data/${dataset}/interactions.*" \
			--people_path "data/${dataset}/people.*" \
			--to_original_graph \
			-k 5 \
			${extra}
	else
		echo "original graph exists"
	fi

	if [ ! -f "${output_dir}/event/meta_graph/${output_name}" ]; then
		echo 'dumping event to meta graph'
		python dump_events_to_json.py \
			--candidate_tree_path ${p} \
			--dirname "${output_dir}/event/meta_graph" \
			--interactions_path "data/${dataset}/interactions.*" \
			--people_path "data/${dataset}/people.*" \
			-k 5 \
			${extra}
	else
		echo "meta graph exists"
	fi
done

echo "dumping event names..."
python dump_all_event_json_names.py \
	${output_dir}/event/meta_graph \
	${output_dir}/event_names.json

chmod -R a+rx ${output_dir}
