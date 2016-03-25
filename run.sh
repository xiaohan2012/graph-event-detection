#! /bin/bash

# ./scripts/synthetic_different_noise_fraction.sh data
# ./scripts/synthetic_different_noise_fraction.sh gen
python tree_util.py
scp -r tmp/tree_inspection/* shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/