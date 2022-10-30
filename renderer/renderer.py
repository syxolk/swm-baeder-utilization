#!/usr/bin/env python3
import os
import sys
from collections import namedtuple
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime, timedelta
import pytz
from jinja2 import Environment, FileSystemLoader
import time
import logging

logger = logging.getLogger("bad-auslastung")
logger.setLevel(logging.DEBUG)

env = Environment(
    loader=FileSystemLoader("./templates")
)
single_org_template = env.get_template("single_org.html")
main_template = env.get_template("main.html")


Organization = namedtuple('Organization', ["name", "df"])
Chart = namedtuple("Chart", ["title", "path"])

def main():
    while True:
        load_data(sys.argv[1], sys.argv[2])
        time.sleep(5*60)


def load_data(input_dir, target_dir):
    orgs = []
    for file in os.listdir(input_dir):
        name = os.path.splitext(os.path.basename(file))[0]
        logger.info(f"Running {name} ...")
        df = pd.read_csv(os.path.join(input_dir, file), header=None, names=["ts", "cnt", "max"], index_col="ts", parse_dates=["ts"])
        df.index = df.index.tz_convert('Europe/Berlin')
        df.loc[df["cnt"] < 0, "cnt"] = 0 # fix data with invalid data
        df["util"] = df["cnt"] / df["max"]
        df["util_percent"] = df["util"] * 100
        org = Organization(name=name, df=df)
        render_org(org, target_dir)
        orgs.append(org)
        logger.info(f"Running {name} ... done")

    render_landing_page(orgs, target_dir)


def render_org(org, target_dir):
    org_dir = os.path.join(target_dir, org.name)
    os.makedirs(org_dir, exist_ok=True)
    charts = [
        render_heatmap_weekday_hour(org, org_dir),
        render_heatmap_week_weekday(org, org_dir),
        render_raw_last_7_days(org, org_dir),
        render_raw_last_24_hours(org, org_dir),
    ]
    plt.close("all")
    render_org_file(org, charts, org_dir)


def render_heatmap_weekday_hour(org, target_dir):
    title = f"Auslastung zu Uhrzeiten je Wochentag (Median-Wert über letzte 8 Wochen)"
    now = datetime.now(pytz.utc)
    now_minus_8_weeks = now - timedelta(weeks=8)
    df = org.df[org.df.index > now_minus_8_weeks]
    max_util = df["cnt"].max()
    grouped_df = df[["cnt"]].groupby(pd.Grouper(freq="1H")).max()
    grouped_df['weekday'] = grouped_df.index.to_series().dt.weekday
    grouped_df['hour'] = grouped_df.index.to_series().dt.hour
    pivot = pd.pivot_table(grouped_df[['weekday', 'hour', 'cnt']], index=['weekday', 'hour'], aggfunc='median')
    pivot = pivot.unstack(level=0)
    pivot = pivot.reindex(columns=[("cnt", i) for i in range(7)])
    detailed_hours = [f"{i:02d} - {i+1:02d}" for i in range(24)]
    day_short_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sns.set_context("talk")
    f, ax = plt.subplots(figsize=(10, 10))
    ax = sns.heatmap(pivot, annot=True, fmt=".0f", linewidths=0, ax=ax, \
        xticklabels=day_short_names, yticklabels=detailed_hours, \
        vmin=0, vmax=max_util, cmap="inferno")
    ax.axes.set_title(title, fontsize=24, y=1.01)
    ax.set(xlabel='Weekday', ylabel='Hour')
    f.tight_layout()
    file = f"heatmap-weekday-hour.svg"
    f.savefig(os.path.join(target_dir, file))
    return Chart(title=title, path=file)


def render_heatmap_week_weekday(org, target_dir):
    max_val = org.df["cnt"].max()
    now = datetime.now(pytz.timezone('Europe/Berlin'))
    now_minus_25_weeks = now - timedelta(weeks=25)
    df = org.df[org.df.index > now_minus_25_weeks]
    grouped_df = df[["cnt"]].groupby(pd.Grouper(freq="D")).max()
    index_isocal = grouped_df.index.to_series().dt.isocalendar()
    grouped_df['week'] = index_isocal.week + index_isocal.year * 100
    grouped_df['weekday'] = grouped_df.index.to_series().dt.weekday
    pivot = pd.pivot_table(grouped_df[['week', 'weekday', 'cnt']], index=['weekday', 'week'], aggfunc='max')
    pivot = pivot.unstack(level=0)
    pivot = pivot.reindex(columns=[("cnt", i) for i in range(7)])
    min_date = now_minus_25_weeks
    max_date = org.df.index.max() + timedelta(days=7)
    week_names = [d.strftime("%V") for d in pd.date_range(start=min_date, end=max_date, freq="W")]
    day_short_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sns.set_context("talk")
    f, ax = plt.subplots(figsize=(10, 10))
    ax = sns.heatmap(pivot, annot=True, fmt=".0f", linewidths=0, ax=ax, \
        xticklabels=day_short_names, yticklabels=week_names)
    #ax.axes.set_title("Heatmap", fontsize=24, y=1.01)
    ax.set(xlabel='Weekday', ylabel='Week of Year')
    f.tight_layout()
    file = "heatmap-week-weekday.svg"
    f.savefig(os.path.join(target_dir, file))
    return Chart(title="Auslastung an Wochentagen über Kalenderwochen (Maximum über letzte 25 Wochen)", path=file)


def render_raw_last_7_days(org, target_dir):
    f, ax = plt.subplots(figsize=(20, 10))
    now = datetime.now(pytz.utc)
    now_minus_7_days = now - timedelta(days=7)
    filtered_df = org.df[org.df.index > now_minus_7_days]
    grouped_df = filtered_df[["cnt", "max"]].groupby(pd.Grouper(freq="15min")).max()
    grouped_df["cnt"].plot.area(ax=ax)
    ax.grid(True)
    #ax.legend()
    ax.set_xlim(now_minus_7_days, now)
    ax.set(xlabel='Date/Time', ylabel='Number of Visitors')
    f.tight_layout()
    file = f"lineplot-7d.svg"
    f.savefig(os.path.join(target_dir, file))
    return Chart(title="Raw Utilization 7 days", path=file)


def render_raw_last_24_hours(org, target_dir):
    f, ax = plt.subplots(figsize=(20, 10))
    now = datetime.now(pytz.utc)
    now_minus_24_hours = now - timedelta(hours=24)
    filtered_df = org.df[org.df.index > now_minus_24_hours]
    grouped_df = filtered_df[["cnt", "max"]].groupby(pd.Grouper(freq="5min")).max()
    grouped_df["cnt"].plot.area(ax=ax)
    ax.grid(True)
    #ax.legend()
    ax.set_xlim(now_minus_24_hours, now)
    ax.set(xlabel='Date/Time', ylabel='Number of Visitors')
    f.tight_layout()
    file = f"lineplot-24h.svg"
    f.savefig(os.path.join(target_dir, file))
    return Chart(title="Raw Utilization 24 hours", path=file)


def format_now():
    return datetime.now(pytz.timezone('Europe/Berlin')).isoformat('T', 'seconds')


def render_org_file(org, charts, target_dir):
    rendered_html = single_org_template.render(
        name=org.name,
        charts=charts,
        created_at=format_now())
    with open(os.path.join(target_dir, "index.html"), "w") as f:
        f.write(rendered_html)


def render_landing_page(orgs, target_dir):
    rendered_html = main_template.render(orgs=orgs, created_at=format_now())
    with open(os.path.join(target_dir, "index.html"), "w") as f:
        f.write(rendered_html)


if __name__ == "__main__":
    main()
