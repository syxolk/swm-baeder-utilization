#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pytz import timezone
import seaborn as sns
import os
from datetime import timedelta

def main():
    label = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    df = pd.read_csv(sys.argv[1], header=None, names=["ts", "cnt", "max"], index_col="ts", parse_dates=["ts"])
    df.index = df.index.tz_convert('Europe/Berlin')

    max_val = df["cnt"].max()
    index_isocal = df.index.to_series().dt.isocalendar()
    df['week'] = index_isocal.week + index_isocal.year * 100
    df['weekday'] = df.index.to_series().dt.weekday
    #df["utilization"] = df["cnt"] / df["max"] * 100
    pivot = pd.pivot_table(df[['week', 'weekday', 'cnt']], index=['weekday', 'week'], aggfunc='max')
    pivot = pivot.unstack(level=0)
    pivot = pivot.reindex(columns=[("cnt", i) for i in range(7)])
    min_date = df.index.min()
    max_date = df.index.max() + timedelta(days=7)
    week_names = [d.strftime("%V") for d in pd.date_range(start=min_date, end=max_date, freq="W")]
    day_short_names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    sns.set_context("talk")
    f, ax = plt.subplots(figsize=(11, 15))
    ax = sns.heatmap(pivot, annot=True, fmt=".0f", linewidths=0, ax=ax, \
        xticklabels=day_short_names, yticklabels=week_names)
    ax.axes.set_title(label, fontsize=24, y=1.01)
    ax.set(xlabel='Wochentag', ylabel='Woche')
    plt.show()


if __name__ == "__main__":
    main()
