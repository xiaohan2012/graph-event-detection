#! /bin/bash

if [ -z $1 ]; then
	echo 'please give dataset name'
	exit -1
fi

ds=$1

rsync -v ukko140:code/lst/data/${ds}/model* data/${ds}
rsync -v ukko140:code/lst/data/${ds}/dict* data/${ds}
rsync -v ukko140:code/lst/data/${ds}/msg_ids.txt data/${ds}
rsync -v ukko140:code/lst/data/${ds}/interactions* data/${ds}
rsync -v ukko140:code/lst/data/${ds}/people* data/${ds}

if  [ ! -d tmp/${ds} ]; then
	mkdir tmp/${ds}
fi
rsync -v ukko140:code/lst/tmp/${ds}/result* tmp/${ds}
# scp ukko140:code/lst/data/${ds}/model* data/${ds}
# scp ukko140:code/lst/data/${ds}/dict* data/${ds}
# scp ukko140:code/lst/data/${ds}/interactions* data/${ds}
# scp ukko140:code/lst/tmp/${ds}/result*.pkl tmp/${ds}
