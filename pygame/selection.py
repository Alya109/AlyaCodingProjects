import pandas as pd
from battle import battlecalc

# file initialization
charcsv = "char.csv"


def importcsv():
    dbfile = pd.read_csv(charcsv)
    return dbfile

def choosechar(dbfile):
    print


