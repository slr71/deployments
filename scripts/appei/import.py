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


def id_from_listing(item: dict, listing: list[dict]) -> bool:
    for listed in listing:
        if listed["name"] == item["name"] and listed["version"] == item["version"]:
            return listed["id"]
    return ""


def clean_tool_for_import(tool: dict):
    if "permission" in tool:
        del tool["permission"]

    if "is_public" in tool:
        del tool["is_public"]

    if "container" in tool:
        if "interactive_apps" in tool["container"]:
            if "id" in tool["container"]["interactive_apps"]:
                del tool["container"]["interactive_apps"]["id"]

        if "image" in tool["container"]:
            if "id" in tool["container"]["image"]:
                del tool["container"]["image"]["id"]

        if "container_ports" in tool["container"]:
            for p in tool["container"]["container_ports"]:
                if "id" in p:
                    del p["id"]


def clean_app_for_import(app: dict):
    delete_keys = [
        "requirements",
        "deleted",
        "pipeline_eligibility",
        "is_favorite",
        "integrator_name",
        "beta",
        "permission",
        "isBlessed",
        "can_favor",
        "disabled",
        "can_rate",
        "suggested_categories",
        "hierarchies",
        "limitChecks",
        "overall_job_type",
        "documentation",
        "categories",
        "is_public",
        "label",
        "step_count",
        "can_run",
        "job_stats",
        "integrator_email",
        "app_type",
        "versions",
        "rating",
    ]
    for d in delete_keys:
        if d in app:
            del app[d]

    if "tools" in app:
        for t in app["tools"]:
            if "implementation" in t:
                if "test" in t["implementation"]:
                    del t["implementation"]["test"]
            if "container" in t:
                if "interactive_apps" in t["container"]:
                    del t["container"]["interactive_apps"]
                if "container_ports" in t["container"]:
                    del t["container"]["container_ports"]
                if "id" in t["container"]:
                    del t["container"]["id"]
                if "image" in t["container"]:
                    if "id" in t["container"]["image"]:
                        del t["container"]["image"]["id"]

    if "groups" in app:
        for g in app["groups"]:
            if "parameters" in g:
                for p in g["parameters"]:
                    if "id" in p:
                        del p["id"]
            if "step_number" in g:
                del g["step_number"]


def import_tool(import_url: str, access_token: str, tool: dict) -> dict:
    payload = json.dumps({"tools": [tool]})

    # Do the import
    res = requests.post(
        import_url,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
        data=payload,
    )

    if not res.ok:
        print(res.text)
        res.raise_for_status()

    return res.json()


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
            new_id = id_from_listing(t, tool_listing)
            if new_id != "":
                t["id"] = new_id
            continue

        print("Importing tool {} {}...".format(t["name"], t["version"]))

        clean_tool_for_import(t)
        tool_res_data = import_tool(tool_import_url, token_data["access_token"], t)
        tool_id = tool_res_data["tool_ids"][0]

        print("Imported tool {} {} as ID {}".format(t["name"], t["version"], tool_id))

        t["id"] = tool_id

    app_import_url = "https://{}/terrain/apps/{}".format(
        args.server, import_data["system_id"]
    )

    if not is_in_listing(import_data, app_listing):
        print("Importing app {} {}".format(import_data["name"], import_data["version"]))

        clean_app_for_import(import_data)

        import_res = requests.post(
            app_import_url,
            headers={
                "Authorization": "Bearer {}".format(token_data["access_token"]),
                "Content-Type": "application/json",
            },
            data=json.dumps(import_data),
        )

        if not import_res.ok:
            print(import_res.text)

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
