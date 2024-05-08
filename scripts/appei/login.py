#!/bin/env python
import argparse
import requests
import os.path
import pathlib
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Login to the Discovery Environment API"
    )
    parser.add_argument(
        "--server",
        action="store",
        default="de.cyverse.org",
        dest="server",
        help="FQDN of the DE server",
        required=True,
    )
    parser.add_argument(
        "--username",
        action="store",
        dest="username",
        help="The admin username",
        required=True,
    )
    parser.add_argument(
        "--password",
        action="store",
        dest="password",
        help="The admin password",
        required=True,
    )
    args = parser.parse_args()

    token_url = "https://{}/terrain/token/keycloak".format(args.server)
    res = requests.get(token_url, auth=(args.username, args.password))
    if res.status_code > 299 or res.status_code < 200:
        print("Error getting token from {}: {}".format(token_url, res.text))
        exit(1)

    config_dir = pathlib.Path(os.path.expanduser("~/.config/cyverse/discoenv/appei"))
    pathlib.Path.mkdir(config_dir, parents=True, exist_ok=True)
    parsed_res = res.json()
    config_path = pathlib.Path.joinpath(config_dir, args.server)
    with open(config_path, "w") as outfile:
        json.dump(parsed_res, outfile)
    print("Access token written to {}".format(config_path))
