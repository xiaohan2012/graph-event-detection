#! /bin/bash

./scripts/synthetic_different_noise_fraction.sh data
./scripts/synthetic_different_noise_fraction.sh gen
python tree_util.py
