#!/usr/bin/env python3
import requests
import datetime
from collections import namedtuple
import time
import json
import sys

Organization = namedtuple('Organization', ["id", "display_name", "name"])

def load_organizations(filename):
    with open(filename) as file:
        data = json.load(file)
    return [Organization(**org) for org in data]

def main():
    orgs = load_organizations(sys.argv[1])

    while True:
        get_and_save_ticos_data(orgs)
        time.sleep(60)


def get_org_name_by_id(orgs, id):
    for x in orgs:
        if x.id == id:
            return x.name
    raise ValueError(f"id not found: {id}")


def get_and_save_ticos_data(orgs):
    data = get_raw_ticos([x.id for x in orgs])
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for x in data:
        name = get_org_name_by_id(orgs, x["organizationUnitId"])
        count = x["personCount"]
        max_count = x["maxPersonCount"]
        with open(f"data/{name}.csv", "a") as file:
            file.write(f"{timestamp},{count},{max_count}\n")


def get_raw_ticos(org_unit_ids):
    params = [
        ("organizationUnitIds", id) for id in org_unit_ids
    ]

    headers = {
        "Abp-TenantId": "69",
        "Abp.TenantId": "69",
        "Sec-GPC": "1",
    }

    r = requests.get("https://functions.api.ticos-systems.cloud/api/gates/counter", headers=headers, params=params)
    return r.json()

if __name__ == "__main__":
    main()
