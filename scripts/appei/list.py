#!/bin/env python

import argparse
import pathlib
import os.path
import json
import requests
from tabulate import tabulate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lists public apps in the Discovery Environment"
    )
    parser.add_argument(
        "--server",
        action="store",
        required=True,
        help="The DE server from which apps should be listed",
        dest="server",
    )
    args = parser.parse_args()

    token_filepath = pathlib.Path(
        os.path.expanduser("~/.config/cyverse/discoenv/appei/{}".format(args.server))
    )
    token_data = None
    with open(token_filepath, "r") as token_file:
        token_data = json.load(token_file)
    if token_data is None:
        print("No token data was found, please run login.py")
        exit(1)
    listing_url = "https://{}/terrain/admin/apps".format(args.server)
    res = requests.get(listing_url, headers={"Authorization": "Bearer {}".format(token_data["access_token"])})
    if res.status_code > 299 or res.status_code < 200:
        print("Status code {}: {}".format(res.status_code, res.text))
        exit(1)
    results = res.json()

    t = []
    for app in results["apps"]:
        t.append([app["id"], app["name"]])
    print(tabulate(t, headers=["ID", "Name"]))
