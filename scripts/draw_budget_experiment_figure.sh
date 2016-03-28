#! /bin/bash

result_paths=("tmp/beefban-budget-experiment/eval_result.pkl" "tmp/enron_small-budget-experiment/eval_result.pkl")
titles=("#beefban" "enron")

python draw_real_data_evaluation_result.py \
    --result_paths ${result_paths[@]} \
    --metric objective_function \
    --titles ${titles[@]} \
    --xlabel B \
    --output_dir tmp/budget_experiment/

scp tmp/budget_experiment/fig.png shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/budget_experiment_together.png
ssh shell.cs.helsinki.fi chmod -R a+rx /cs/home/hxiao/public_html/figures/

