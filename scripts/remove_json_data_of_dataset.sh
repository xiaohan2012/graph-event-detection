#! /bin/bash

root="/cs/home/hxiao/public_html/event_html/data"

if [ -z $1 ]; then
	echo 'please give dataset name'
	exit -1
fi

ds=$1


# rm -r "${root}/${ds}/event/meta_graph/"
# rm -r "${root}/${ds}/event/original_graph/"
rm -r "${root}/${ds}/timeline/"

