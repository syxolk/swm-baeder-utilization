#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import itertools
import datetime
from pytz import timezone
from matplotlib.dates import HourLocator, MinuteLocator

def main():
    #f, axes = plt.subplots(len(sys.argv[1:]), 1, sharex=True)
    markers = itertools.cycle(("o", "s", "v", "^", "X", "D", "P"))
    for (file, marker) in zip(sys.argv[1:], markers):
        df = pd.read_csv(file, header=None, names=["ts", "cnt", "max"], index_col="ts", parse_dates=["ts"])
        df.index = df.index.tz_convert('Europe/Berlin')
        df["utilization"] = df["cnt"] / df["max"]
        #df = df[df.index >= datetime.datetime(2020, 10,16,6,30, tzinfo=timezone("Europe/Berlin"))]
        label = os.path.splitext(os.path.basename(file))[0]
        #df["utilization"].groupby(pd.Grouper(freq="15min")).max().plot(grid=True, label=label, marker=marker)
        #df["utilization"].rolling("2h").max().plot(grid=True, label=label, marker=marker)
        #first_cnt = df["cnt"].iloc[0]
        #df["cleaned_cnt"] = df["cnt"].diff()
        #df[df["cleaned_cnt"].abs() > 30] = 0
        #df.iloc[df.columns.get_loc("cleaned_cnt"), 0] = first_cnt
        #print(df)
        #df["cleaned_cnt"] = df["cleaned_cnt"].cumsum()
        #df["cleaned_cnt"].plot(grid=True, label=label, marker=marker, x_compat=True)
        plt.minorticks_on()
        df["cnt"].plot(label=label, marker=marker)
        plt.grid(axis="both")

        #df["derived"] = df["cnt"].diff() / df.index.to_series().diff().dt.total_seconds() * 60
        #df["derived"].plot(label=label, x_compat=True, grid=True, marker=marker)
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #ax = plt.gca()
    #ax.xaxis.set_major_locator(HourLocator(byhour=range(24), interval=3, tz=timezone("Europe/Berlin")))
    #ax.xaxis.set_minor_locator(HourLocator(byhour=range(24), interval=1, tz=timezone("Europe/Berlin")))
    plt.legend()
    plt.ylabel("Visitors")
    plt.xlabel("Date/Time")
    plt.tight_layout()
    plt.show()
    #plt.savefig("baeder.svg")

if __name__ == "__main__":
    main()
