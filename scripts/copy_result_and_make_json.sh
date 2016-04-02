#! /bin/bash

if [ -z $1 ]; then
	echo 'please give dataset name'
	exit -1
fi

ds=$1

./scripts/copy_result_from_ukko.sh $ds

./scripts/make_json_data_for_timeline.sh $ds
./scripts/make_json_data_for_d3.sh $ds
