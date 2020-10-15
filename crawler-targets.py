#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
from slugify import slugify

# https://github.com/un33k/python-slugify

URLS = [
    "https://www.swm.de/privatkunden/m-baeder/schwimmen/hallenbaeder.html",
    "https://www.swm.de/privatkunden/m-baeder/sauna.html",
]

def main():
    orgs = []
    for url in URLS:
        orgs += crawl_url(url)

    orgs.sort(key=lambda x: x["display_name"])

    with open("organizations.json", "w") as file:
        json.dump(orgs, file, indent=2)


def crawl_url(url):
    orgs = []
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    for ticos_el in soup.select("multiple-ticos-bar-counter"):
        ids = json.loads(ticos_el["organizations"])
        displays = json.loads(ticos_el["displays"])
        orgs += [dict(id=id, name=slugify(name), display_name=name) for (id, name) in zip(ids, displays)]
    return orgs


if __name__ == "__main__":
    main()
