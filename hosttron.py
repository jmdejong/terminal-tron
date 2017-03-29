#! /usr/bin/python3

import sys

if sys.version_info[0] < 3:
    print("This game is written in python 3.\nRun 'python3 "+sys.argv[0]+"' or './"+sys.argv[0]+"'")
    sys.exit(-1)

sys.path.append(sys.path[0]+"/server/")
sys.path.append(sys.path[0]+"/shared/")
import trongame
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socket', help='The socket file to listen to.\nThis is useful if another server is already using the default socket file or if it wasn\'t removed properly.\nWARNING: if the given file exists it will be overwritten.\nDefaults to /tmp/tron_socket', default="/tmp/tron_socket")
args = parser.parse_args()

try:
    while True:
        try:
            trongame.TronGame().start(args.socket)
        except Exception as err:
            # In case of a normal exception, restart instead of die
            print(err)
finally:
    # in case of an abnormal exception, do the cleanup
    print("base exception")
    try:
        os.unlink(args.socket)
    except FileNotFoundError:
        if os.path.exists(args.socket):
            raise
