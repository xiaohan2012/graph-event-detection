from glob import glob
import os
import sys
import json


def main():
    dirname = sys.argv[1]
    print json.dumps(glob(os.path.join(dirname, "result-*.json")))
    
if __name__ == '__main__':
    main()
