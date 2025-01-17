import sys, os
ROOT_PATH = os.path.abspath(".").split("src")[0]
module_path = os.path.abspath(os.path.join(ROOT_PATH+"/src/utils/"))
if module_path not in sys.path:
    sys.path.append(module_path)

import time
import utilities
import prints
import plots
import pandas as pd
from configs import getConfig

def main(filename, column, target_file):
    print("Loading file {}".format(filename))
    df_iris = pd.read_csv(filename).drop(column, axis=1)
    print("Writing file {}".format(target_file))
    df_iris.to_csv(target_file, index=False)

pyName = "dropColumn.py"
arguments = [
    "- filename (string)",
    "- target filename (string)",
    "- name of column (string)",
]

# usage: python dropColumn.py file targetfile column
if __name__ == "__main__":
    start_time = time.time()
    prints.printEmptyLine()
    
    print("Running", pyName)
    print("Prints dataframe")
    prints.printEmptyLine()

    try:
        filename = sys.argv[1]
        target_file = sys.argv[2]
        column = sys.argv[3]
    except IndexError:
        print(pyName, "was called with inappropriate arguments")
        print("Please provide the following arguments:")
        for argument in arguments:
            print(argument)
        sys.exit()

    main(filename, column, target_file)

    prints.printEmptyLine()
    print("Running of", pyName, "finished in", time.time() - start_time, "seconds")
    prints.printEmptyLine()