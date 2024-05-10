#!/bin/env python

import argparse
import json
import requests
import pathlib
import os.path


def list_tools(server: str, access_token: str) -> dict:
    listing_url = "https://{}/terrain/admin/tools".format(server)
    res = requests.get(
        listing_url, headers={"Authorization": "Bearer {}".format(access_token)}
    )
    res.raise_for_status()
    return res.json()["tools"]


def list_apps(server: str, access_token: str, name: str) -> dict:
    listing_url = "https://{}/terrain/admin/apps".format(server)
    res = requests.get(
        listing_url,
        headers={"Authorization": "Bearer {}".format(access_token)},
        params={"search": name},
    )
    res.raise_for_status()
    return res.json()["apps"]


def is_in_listing(item: dict, listing: list[dict]) -> bool:
    for listed in listing:
        if listed["name"] == item["name"] and listed["version"] == item["version"]:
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import app/tool definitions into a DE instance"
    )
    parser.add_argument(
        "--server",
        action="store",
        required=True,
        dest="server",
        help="The server to import apps into",
    )
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        required=True,
        dest="input",
        help="The file containing the JSON defining an app and its tools",
    )
    args = parser.parse_args()

    # Read the access_token from the config directory.
    token_filepath = pathlib.Path(
        os.path.expanduser("~/.config/cyverse/discoenv/appei/{}".format(args.server))
    )

    token_data = None
    with open(token_filepath, "r") as token_file:
        token_data = json.load(token_file)

    if token_data is None:
        print("No token data was found, please run login.py")
        exit(1)

    print("Importing app and tools into server {}".format(args.server))

    # Read the import data from the input file.
    import_data = None
    with open(args.input, "r") as infile:
        import_data = json.load(infile)

    if import_data is None:
        print("No import data read from {}".format(args.input))
        exit(1)

    # Get a listing of the tools already in the DE.
    tool_listing = list_tools(args.server, token_data["access_token"])
    app_listing = list_apps(
        args.server, token_data["access_token"], import_data["name"]
    )

    # First, import the tools and get the IDs for them.
    tool_import_url = "https://{}/terrain/admin/tools".format(args.server)
    for t in import_data["tools"]:
        # Don't bother re-importing a tool if it's already in the DE.
        if is_in_listing(t, tool_listing):
            print("Skipping import of {} {}".format(t["name"], t["version"]))
            continue

        print("Importing tool {} {}".format(t["name"], t["version"]))

        # Do the import
        tool_res = requests.post(
            tool_import_url,
            headers={"Authorization": "Bearer {}".format(token_data["access_token"])},
            data=t,
        )
        tool_res.raise_for_status()
        tool_res_data = tool_res.json()
        tool_id = tool_res_data["tool_ids"][0]
        t["id"] = tool_id

    app_import_url = "https://{}/terrain/apps/{}".format(
        args.server, import_data["system_id"]
    )
    if not is_in_listing(import_data, app_listing):
        print("Importing app {} {}".format(import_data["name"], import_data["version"]))
        import_url = "https://{}/terrain/apps/{}".format(import_data["system_id"])
        import_res = requests.post(
            import_url,
            headers={"Authorization": "Bearer {}".format(token_data["access_token"])},
            data=import_data,
        )
        import_res.raise_for_status()
        print(
            "Done importing app {} {}".format(
                import_data["name"], import_data["version"]
            )
        )
    else:
        print(
            "Skipping import of {} {}".format(
                import_data["name"], import_data["version"]
            )
        )
