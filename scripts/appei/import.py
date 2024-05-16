#!/bin/env python

import argparse
import json
import requests
import pathlib
import os.path
from collections import Counter


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


def list_private_apps(server: str, access_token: str, name: str) -> dict:
    u = "https://{}/terrain/apps".format(server)
    res = requests.get(
        u,
        headers={"Authorization": "Bearer {}".format(access_token)},
        params={"search": name},
    )
    if not res.ok:
        print(res.text)
    res.raise_for_status()
    return res.json()["apps"]


def id_from_listing(item: dict, listing: list[dict]) -> bool:
    for listed in listing:
        if listed["name"] == item["name"] and listed["version"] == item["version"]:
            return listed["id"]
    return ""


def create_app_submission(app: dict) -> dict:
    submission = {
        "avus": [],
    }
    top_level = [
        "integration_date",
        "description",
        "version_id",
        "name",
        "system_id",
        "references",
        "id",
        "edited_date",
    ]
    for t in top_level:
        submission[t] = app[t]

    submission["documentation"] = app["documentation"]["documentation"]

    return submission


def publish_app(
    server: str, access_token: str, system_id: str, submission: dict
) -> dict:
    u = "https://{}/terrain/apps/{}/{}/publish".format(
        server, system_id, submission["id"]
    )
    res = requests.post(
        u,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
        data=json.dumps(submission),
    )
    if not res.ok:
        print(res.text)
    res.raise_for_status()


def bless_app(server: str, access_token: str, system_id: str, app_id: str):
    u = "https://{}/terrain/admin/apps/{}/{}/blessing".format(server, system_id, app_id)

    res = requests.post(
        u,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
    )

    if not res.ok:
        print(res.text)

    res.raise_for_status()


def import_app(server: str, access_token: str, system_id: str, import_data: dict):
    app_import_url = "https://{}/terrain/apps/{}".format(server, system_id)

    import_res = requests.post(
        app_import_url,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
        data=json.dumps(import_data),
    )

    if not import_res.ok:
        print(import_res.text)

    import_res.raise_for_status()
    return import_res.json()


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


def clean_app_for_import(app: dict) -> dict:
    cleaned = app.copy()
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
        if d in cleaned:
            del cleaned[d]

    if "tools" in cleaned:
        for t in cleaned["tools"]:
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

    if "groups" in cleaned:
        for g in cleaned["groups"]:
            if "parameters" in g:
                for p in g["parameters"]:
                    if "id" in p:
                        del p["id"]

                    # This should really be done in the API, but since it's not
                    # it has to be included here. Adapted from similar code in Sonora.
                    match p["type"]:
                        case "Flag":
                            if "defaultValue" not in p:
                                p["defaultValue"] = False
                            if "name" not in p:
                                p["name"] = {
                                    "checked": {"option": "", "value": ""},
                                    "unchecked": {"option": "", "value": ""},
                                }

                        case "TextSelection":
                            if "arguments" not in p:
                                p["arguments"] = []
                            if "defaultValue" not in p:
                                p["defaultValue"] = ""
                            if "required" not in p:
                                p["required"] = False
                            if "omit_if_blank" not in p:
                                p["omit_if_blank"] = False

                        case (
                            "MultiFileOutput"
                            | "FileInput"
                            | "FolderInput"
                            | "FileOutput"
                            | "FolderOutput"
                        ):
                            p["defaultValue"] = ""
                            p["required"] = False
                            p["omit_if_blank"] = False
                            p["file_parameters"] = {
                                "is_implicit": False,
                                "data_source": "file",
                                "format": "Unspecified",
                                "file_info_type": "File",
                            }
                        case "MultiFileSelector":
                            p["defaultValue"] = []
                            p["required"] = False
                            p["omit_if_blank"] = False
                            p["file_parameters"] = {
                                "data_source": "file",
                                "file_info_type": "File",
                                "format": "Unspecified",
                                "is_implicit": False,
                                "repeat_option_flag": False,
                            }
                        case _:
                            if "file_parameters" in p:
                                del p["file_parameters"]
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


def app_details(
    server: str, access_token: str, system_id: str, app_id: str
) -> list[dict]:
    u = "https://{}/terrain/apps/{}/{}/details".format(server, system_id, app_id)

    res = requests.get(
        u,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
    )
    if not res.ok:
        print(res.text)
    res.raise_for_status()

    return res.json()


def app_metadata(server: str, access_token: str, app_id: str) -> list[dict]:
    u = "https://{}/terrain/admin/apps/{}/metadata".format(server, app_id)

    res = requests.get(
        u,
        headers={
            "Authorization": "Bearer {}".format(access_token),
        },
    )

    if not res.ok:
        print(res.text)

    res.raise_for_status()

    return res.json()


def set_app_metadata(server: str, access_token: str, app_id: str, avus: list[dict]):
    u = "https://{}/terrain/admin/apps/{}/metadata".format(server, app_id)

    res = requests.put(
        u,
        headers={
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        },
        data=json.dumps({"avus": avus}),
    )

    if not res.ok:
        print(res.text)

    res.raise_for_status()


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

    access_token = token_data["access_token"]
    system_id = import_data["system_id"]
    app_name = import_data["name"]
    app_version = import_data["version"]

    # Get a listing of the tools already in the DE.
    tool_listing = list_tools(args.server, access_token)
    app_listing = list_apps(args.server, access_token, app_name)
    private_listing = list_private_apps(args.server, access_token, app_name)

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
        tool_res_data = import_tool(tool_import_url, access_token, t)
        tool_id = tool_res_data["tool_ids"][0]

        print("Imported tool {} {} as ID {}".format(t["name"], t["version"], tool_id))

        t["id"] = tool_id

    app_id = None

    # If the app isn't in the public listing, import it.
    if not is_in_listing(import_data, app_listing):
        print("Importing app {} {}".format(app_name, app_version))

        submission = create_app_submission(import_data)
        cleaned_app = clean_app_for_import(import_data)

        # If the app isn't in the user's private app listing, import it.
        if not is_in_listing(cleaned_app, private_listing):
            app_id = import_app(args.server, access_token, system_id, cleaned_app)
        else:
            # Otherwise get the id from the private listing.
            app_id = [
                a["id"]
                for a in private_listing
                if a["name"] == app_name and a["version"] == app_version
            ][0]

        # The ID for the submission needs to match the ID of the imported app.
        submission["id"] = app_id

        # Request that the app be made public.
        publish_app(
            args.server,
            access_token,
            system_id,
            submission,
        )

        # Make the app public
        bless_app(args.server, access_token, system_id, app_id)

        print("Done importing app {} {}".format(app_name, app_version))

    else:
        print("Skipping import of {} {}".format(app_name, app_version))

        # If we're here then the app was in the public listing and that
        # should have the app_id value that we need for later ops.
        app_id = [
            a["id"]
            for a in app_listing
            if a["name"] == app_name and a["version"] == app_version
        ][0]

    # Get the current list of AVUs on the app.
    app_avus = app_metadata(args.server, access_token, app_id)["avus"]

    # Remove the beta AVU.
    new_avus = [
        avu
        for avu in app_avus
        if not (avu["attr"] == "n2t.net/ark:/99152/h1459" and avu["value"] == "beta")
    ]

    # Set the new list of AVUs if it's different from the original list.
    if len(app_avus) != len(new_avus):
        print("Removing the beta status from the imported app...")
        set_app_metadata(args.server, access_token, app_id, new_avus)
        print("Done removing the beta status from the imported app.")
    else:
        print("Skipping removal of beta status.")
