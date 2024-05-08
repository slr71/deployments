#!/bin/env python

import argparse
import pathlib
import os.path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Logs out from the Discovery Environment"
    )
    parser.add_argument(
        "--server",
        action="store",
        help="DE server to log out from",
        dest="server",
        required=True,
    )
    args = parser.parse_args()

    config_path = pathlib.Path(
        os.path.expanduser("~/.config/cyverse/discoenv/appei/{}".format(args.server))
    )

    if config_path.exists():
        config_path.unlink()
        print("Deleted file {}".format(config_path))
    else:
        print("File {} does not exist, no logout necessary.".format(config_path))
