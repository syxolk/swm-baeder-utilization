#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def main():
    for file in sys.argv[1:]:
        df = pd.read_csv(file, header=None, names=["ts", "cnt", "max"], index_col="ts", parse_dates=["ts"])
        df.index = df.index.tz_convert('Europe/Berlin')
        df["cnt"].plot(grid=True, label=os.path.splitext(os.path.basename(file))[0])
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1))
    plt.ylabel("Visitors")
    plt.xlabel("Date/Time")
    plt.tight_layout()
    plt.show()
    #plt.savefig("baeder.svg")

if __name__ == "__main__":
    main()
