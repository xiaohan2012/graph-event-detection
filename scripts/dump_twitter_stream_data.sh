#! /bin/bash

if [ -z $1 ]; then
    echo 'col name empty'
    exit -1
fi
col=$1

if  [ ! -d data/$col ]; then
    mkdir data/$col
fi

python mongo2df.py -d twitter_stream \
    -c  $col \
    -o data/$col


