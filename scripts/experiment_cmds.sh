python gen_candidate_trees.py --method lst --dist euclidean --U=0.05 --lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics
python gen_candidate_trees.py --method greedy --dist euclidean --U=0.05 --lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics
python gen_candidate_trees.py --method random --dist euclidean --U=0.05 --lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics
python gen_candidate_trees.py --method lst --dist euclidean --dij  --U=0.05 --lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics
