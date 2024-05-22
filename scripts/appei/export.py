#!/bin/env python

import argparse
import pathlib
import os.path
import json
import requests
from deepmerge import always_merger as merger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export an app and tool JSON description"
    )
    parser.add_argument(
        "--server",
        action="store",
        required=True,
        dest="server",
        help="The server to export definitions from",
    )
    parser.add_argument(
        "-i",
        "--id",
        action="store",
        required=True,
        dest="id",
        help="The ID of the app to export",
    )
    parser.add_argument(
        "-s",
        "--system-id",
        action="store",
        required=False,
        default="de",
        dest="system_id",
        help="The system-id to use when exporting an app",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        required=False,
        dest="output",
        help="The file to store app and tool definitions in",
    )
    args = parser.parse_args()

    # Get the token data for auth
    token_filepath = pathlib.Path(
        os.path.expanduser("~/.config/cyverse/discoenv/appei/{}".format(args.server))
    )
    token_data = None
    with open(token_filepath, "r") as token_file:
        token_data = json.load(token_file)
    if token_data is None:
        print("No token data was found, please run login.py")
        exit(1)

    # Get the base app info
    details_url = "https://{}/terrain/admin/apps/{}/{}/details".format(
        args.server, args.system_id, args.id
    )
    res = requests.get(
        details_url,
        headers={"Authorization": "Bearer {}".format(token_data["access_token"])},
    )
    res.raise_for_status()
    app_details = res.json()

    # Get extra app info
    desc_url = "https://{}/terrain/apps/{}/{}".format(
        args.server, args.system_id, args.id
    )
    desc_res = requests.get(
        desc_url,
        headers={"Authorization": "Bearer {}".format(token_data["access_token"])},
    )
    desc_res.raise_for_status()
    desc_data = desc_res.json()

    # Merge the extra app info into the base dict.
    app = merger.merge(app_details, desc_data)

    # Lookup and merge extra tool details
    tool_url_template = "https://{}/terrain/admin/tools/{}"
    for tool in app["tools"]:
        t = tool["id"]
        tool_url = tool_url_template.format(args.server, t)
        tool_response = requests.get(
            tool_url,
            headers={"Authorization": "Bearer {}".format(token_data["access_token"])},
        )
        tool_response.raise_for_status()
        tool = merger.merge(tool, tool_response.json())

    # Write out the fully merged object
    if args.output != None:
        output_path = os.path.expanduser(args.output)
        output_path = os.path.expandvars(output_path)
        output_path = pathlib.Path(output_path)
        with open(output_path, "w") as output_file:
            json.dump(app, output_file, sort_keys=True, indent=2)
    else:
        print(json.dumps(app, sort_keys=True, indent=2))
