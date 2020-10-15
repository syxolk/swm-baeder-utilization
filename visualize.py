#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import sys

def main():
    df = pd.read_csv(sys.argv[1], header=None, names=["ts", "cnt", "max"], index_col="ts", parse_dates=["ts"])
    df.plot(ylim=[0, df["max"].max()*1.1], grid=True)
    plt.show()

if __name__ == "__main__":
    main()
