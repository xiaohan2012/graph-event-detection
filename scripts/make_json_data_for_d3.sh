# Generate the json data for top events
# 4 types of data for each candidate tree
# - event with context
#   - meta-graph
#   - original graph
# - event without context
#   - meta-graph
#   - original graph

if [ -z $1 ]; then
	echo "dataset name is not given"
	exit -1
fi

if [ -z $2 ]; then
	echo "events pickle dir is not given"
	exit -1
fi

if [ -z $3 ]; then
	echo "interaction json path is not given"
	exit -1
fi

dataset_name=$1
pickle_dir=$2
interactions_path=$3
output_dir="html/data/${dataset_name}"

if [ -d $output_dir ]; then
	echo "rm -rf ${output_dir}"
	rm -rf ${output_dir}
fi

for p in $(ls $pickle_dir); do
	echo "${p}"
	# contexted events
	python dump_contexted_events_to_json.py \
		--interactions_path ${interactions_path} \
		--candidate_tree_path ${p} \
		--dirname "${output_dir}/contexted_event/original_graph" \
		--to_original_graph
	python dump_contexted_events_to_json.py \
		--interactions_path ${interactions_path} \
		--candidate_tree_path ${p} \
		--dirname "${output_dir}/contexted_event/meta_graph"

	# just events
	python dump_events_to_json.py \
		--candidate_tree_path ${p} \
		--dirname "${output_dir}/event/original_graph" \
		--to_original_graph
	python dump_events_to_json.py \
		--candidate_tree_path ${p} \
		--dirname "${output_dir}/event/meta_graph"
done

python dump_all_event_json_names.py ${output_dir}/event/meta_graph ${output_dir}/event_names.json
