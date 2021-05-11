#!/usr/bin/env python3

#%% Imports
import os
from sys import argv
import requests
from pprint import pprint
import argparse
from tqdm import tqdm


#%% API Access Functions
def build_url(host, set=None, dir=None):
    url = "http://" + host + "/files"

    if set is not None:
        url += "/{:04d}SET".format(set)

    if dir is not None:
        url += "/{:03d}".format(dir)

    return url


def _print_list(l):
    _st = ""
    for it in l:
        _st += it + "\n"
    print(_st)


def process_response(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError(
            "Returned {} status code for URL {}".format(resp.status_code, url)
        )
    return resp


def get_dirs(host, set=None):
    url = build_url(host, set)
    resp = process_response(url)
    data = resp.json()
    return data["directories"]


def get_file_list(host, set, dir):
    url = build_url(host, set, dir)
    resp = process_response(url)
    data = resp.json()
    file_list = [x["name"] for x in data["files"]]
    return file_list


def download_setfiles(host, set, dir, filename, output_path):
    url = build_url(host, set, dir) + "/" + filename
    resp = process_response(url)
    with open(os.path.join(output_path, filename), "wb") as f:
        f.write(resp.content)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Access MicaSense camera API.")

    parser.add_argument(
        "--host",
        help="MicaSense camera hostname or IP address",
        default="192.168.10.254",
    )

    subparsers = parser.add_subparsers(dest="command")

    getcmd = subparsers.add_parser("get", help="Get info")
    getcmd.add_argument(
        "asset", help="Asset to get info for", choices=("sets", "setdirs", "setfiles")
    )
    getcmd.add_argument("--set", type=int, help="Set of images", default=0)
    getcmd.add_argument("--dir", type=int, help="Dir of images", default=0)

    downcmd = subparsers.add_parser("download", help="Download images")
    downcmd.add_argument(
        "--output-path", required=True, help="Path to a folder where to save images"
    )
    downcmd.add_argument("--set", type=int, help="Set of images", default=0)
    downcmd.add_argument(
        "--dir", required=False, type=int, help="Dir of images", default=0
    )
    return parser.parse_args()


# %%
if __name__ == "__main__":
    args = parse_arguments()
    host = args.host
    if args.command == "get":
        if args.asset == "sets":
            print("Sets available:")
            _print_list(get_dirs(host))
        elif args.asset == "setdirs":
            print("Dirs of set {}:".format(args.set))
            _print_list(get_dirs(host, args.set))
        elif args.asset == "setfiles":
            print("Files of set {} and dir {}:".format(args.set, args.dir))
            _print_list(get_file_list(host, args.set, args.dir))
    elif args.command == "download":
        output_path = args.output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print("Downloading files of set {} and dir {}".format(args.set, args.dir))
        file_list = get_file_list(host, args.set, args.dir)
        for f in tqdm(file_list):
            download_setfiles(host, args.set, args.dir, f, output_path)
        print("All files have been downloaded")

# %%
