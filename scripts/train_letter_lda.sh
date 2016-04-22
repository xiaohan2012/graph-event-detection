#! /bin/bash

# parallel ./scripts/train_lda.sh {} dump_msg 20 50 -1 \
#     ::: letter-1420-1499 \
#     letter-1500-1569 \
#     letter-1350-1419 \
#     letter-1570-1639 \
#     letter-1640-1710


if [ -z $1 ]; then
    arg="nothing"
else
    arg="dump_msg"
fi
./scripts/train_lda.sh letter_18c $arg 20 200 -1 
# "-s /cs/home/hxiao/code/lst/data/letter_18c_stopwords.txt"