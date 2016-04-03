#! /bin/bash

result_paths=("tmp/beefban-budget-experiment/eval_result.pkl" "tmp/baltimore-budget-experiment/eval_result.pkl" "tmp/ukraine-budget-experiment/eval_result.pkl" "tmp/enron_small-budget-experiment/eval_result.pkl")
titles=("#beefban" "#baltimore" "#ukraine" "enron")

metrics=("treesize-objective-mean" "treesize-objective-median" "setcover-objective")

for metric in ${metrics[@]}; do
    echo $metric
    python draw_real_data_evaluation_result.py \
	--result_paths ${result_paths[@]} \
	--metric $metric \
	--titles ${titles[@]} \
	--xlabel B \
	--output_path tmp/budget_experiment/budget-experiment-${metric}.png \
	--legend_in_which_subplot 4
done


scp tmp/budget_experiment/*.png shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/
ssh shell.cs.helsinki.fi chmod -R a+rx /cs/home/hxiao/public_html/figures/

