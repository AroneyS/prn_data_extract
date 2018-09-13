import sys, os
import numpy as np
import pandas as pd


try:
    infile = sys.argv[1]
except:
    pass

classifications_all = pd.read_csv(infile)

print(classifications_all.headers)