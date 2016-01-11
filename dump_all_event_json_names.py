from glob import glob
import os
import sys
from util import json_dump


def main():
    dirname = sys.argv[1]
    output_path = sys.argv[2]
    names = map(os.path.basename,
                glob(os.path.join(dirname, "result-*.json")))
    json_dump(names, output_path)
    
if __name__ == '__main__':
    main()
