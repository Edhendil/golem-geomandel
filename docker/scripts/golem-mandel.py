import sys
import os

import json

INPUT_PATH = '/golem/work/task.json'

def main(argv):
    with open(INPUT_PATH) as json_file:
        task = json.load(json_file)
        command: str = f'python /golem/scripts/mandel.py -x {task["x"]} -y {task["y"]} -z {task["zoom"]}'
        os.system(command)

if __name__ == "__main__":
   main(sys.argv[1:])
