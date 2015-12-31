#!/bin/bash

cat scripts/experiment_cmds.sh | parallel -S ukko180,ukko161,ukko165,ukko156 --workdir . --jobs 4
