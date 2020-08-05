#!/usr/bin/env python3

#%% Imports
import os
from sys import argv
import requests
from pprint import pprint
import argparse
from tqdm import tqdm

#%% API Access Functions
def process_response(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError("Returned {} status code for URL {}".format(resp.status_code, url))
    return resp

def get_sets(host):
    url = 'http://' + host + '/files'
    resp = process_response(url)
    data = resp.json()
    return data['directories']
    
def get_file_list(host, set):
    url = 'http://' + host + '/files' + '/{:04d}SET'.format(set) + '/000'
    resp = process_response(url)
    data = resp.json()
    file_list = [ x['name'] for x in data['files'] ]
    return file_list

def download_set_file(host, set, filename, output_path):
    url = 'http://' + host + '/files' + '/{:04d}SET'.format(set) + '/000' + '/' + filename
    resp = process_response(url)
    with open(os.path.join(output_path, filename), 'wb') as f:
        f.write(resp.content)

def _print_list(l):
    _st = ''
    for it in l:
        _st += it + '\n'
    print(_st)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Access MicaSense camera API.")
    
    parser.add_argument("--host", required=True,
                      help="MicaSense camera hostname or IP address")

    subparsers = parser.add_subparsers(dest='command')

    getcmd = subparsers.add_parser('get', help='Get info')
    getcmd.add_argument('asset', help="Asset to get info for", choices=('sets', 'setfiles'))
    getcmd.add_argument("--set", required=False, type=int,
                    help="Set of images")

    downcmd = subparsers.add_parser('download', help='Download images')

    downcmd.add_argument("--output-path", required=True,
                      help="Path to a folder where to save images")
    downcmd.add_argument("--set", required=True, type=int,
                      help="Set of images")
    return parser.parse_args()

# %% 
if __name__ == "__main__":
    args = parse_arguments()
    host = args.host
    if args.command == 'get':
        if args.asset == 'sets':
            _print_list(get_sets(host))
        elif args.asset == 'setfiles':
            if args.set is not None:
                _print_list(get_file_list(host, args.set))
            else:
                raise AssertionError('No set given')
    elif args.command == 'download':
        output_path = args.output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        file_list = get_file_list(host, args.set)
        for f in tqdm(file_list):
            download_set_file(host, args.set, f, output_path)
        print("All files have been downloaded")
        
# %%
