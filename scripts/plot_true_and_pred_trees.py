#! /bin/bash

python tree_util.py
scp -r tmp/tree_inspection/* shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/
