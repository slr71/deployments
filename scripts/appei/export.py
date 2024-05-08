#!/bin/env python

import argparse
import pathlib
import os.path
import json
import requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export an app and tool JSON description")
    parser.add_argument("--server", action="store", required=True, dest="server", help="The server to export definitions from")
    parser.add_argument("-i", "--id", action="store", required=True, dest="id", help="The ID of the app to export")
    parser.add_argument("-s", "--system-id", action="store", required=False, default="de", dest="system_id", help="The system-id to use when exporting an app")
    parser.add_argument("-o", "--output", action="store", required=False, dest="output", help="The file to store app and tool definitions in")
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

    export_url = "https://{}/terrain/apps/{}/{}".format(args.server, args.system_id, args.id)
    res = requests.get(export_url, headers={"Authorization" : "Bearer {}".format(token_data["access_token"])})
    if res.status_code > 299 or res.status_code < 200:
        print("Status code {}: {}".format(res.status_code, res.text))
        exit(1)
    results = res.json()

    if args.output != None:
        output_path = os.path.expanduser(args.output)
        output_path = os.path.expandvars(output_path)
        output_path = pathlib.Path(output_path)
        with open(output_path, "w") as output_file:
            json.dump(results, output_file, sort_keys=True, indent=2)
    else:
        print(json.dumps(results, sort_keys=True, indent=2))