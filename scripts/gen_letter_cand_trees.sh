#! /bin/bash

datasets=(letter-1420-1499  letter-1500-1569 letter-1350-1419 letter-1570-1639 letter-1640-1710)

for ds in ${datasets[@]}; do
    ./scripts/gen_cand_trees.sh ${ds} 50.0 300 "--weight_for_topics 1.0 --weight_for_bow 0.0 --days 3650"
done
