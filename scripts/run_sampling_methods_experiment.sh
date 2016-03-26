#! /bin/bash

dataset=$1

if [ -z $dataset ]; then
    exit -1
fi
# ./scripts/sampling_methods_experiment.sh  gen
./scripts/sampling_methods_experiment.sh  $dataset eval
./scripts/sampling_methods_experiment.sh  $dataset viz