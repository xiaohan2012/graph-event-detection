import os

from nose.tools import assert_true
from subprocess import check_output

from test_util import CURDIR, remove_tmp_data


def test_cmd():
    cmd = """python {} --n_topics 2 \
    --n_iters 1 \
    --lda_update_every 1 \
    --lda_chunksize 100 \
    --id2token {} \
    --mm_path  {}\
    --model_prefix {} """.format(
        os.path.join(CURDIR, 'lda/lda.py'),
        os.path.join(CURDIR, 'test/data/id2token.pkl'),
        os.path.join(CURDIR, 'test/data/messages.mm'),
        os.path.join(CURDIR, 'test/data/tmp/model')
    )
    print(cmd)
    output = check_output(cmd, shell=True)
    print(output)
    assert_true("traceback" not in output.lower())

    remove_tmp_data(os.path.join(CURDIR, 'test/data/tmp'))
