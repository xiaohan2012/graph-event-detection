#! /bin/bash

result_paths=("tmp/beefban-sampling-scheme-experiment/eval_result.pk" "tmp/baltimore-sampling-scheme-experiment/eval_result.pk" "tmp/ukraine-sampling-scheme-experiment/eval_result.pk" "tmp/enron_small-sampling-scheme-experiment/eval_result.pk")
titles=("#beefban" "#baltimore" "#ukraine" "enron")

python draw_real_data_evaluation_result.py \
    --result_paths ${result_paths[@]} \
    --metric k_setcover_obj \
    --titles ${titles[@]} \
    --xlabel B \
    --output_path tmp/sampler_experiment/fig.png \
    --legend_in_which_subplot 4 \
    --nrows 1 \
    --ncols 4 \
    --figure_width 20 \
    --figure_height 5

scp tmp/sampler_experiment/fig.png shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/sampler_experiment_together.png
ssh shell.cs.helsinki.fi chmod -R a+rx /cs/home/hxiao/public_html/figures/

