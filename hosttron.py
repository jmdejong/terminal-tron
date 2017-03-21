#! /usr/bin/python3

import sys

if sys.version_info[0] < 3:
    print("This game is written in python 3.\nRun 'python3 "+sys.argv[0]+"' or './"+sys.argv[0]+"'")
    sys.exit(-1)

sys.path.append("./server/")
sys.path.append("./shared/")

import tronserver
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socket', help='The socket file to listen to. Use this if the default socket exists already.\nWARNING: if the given file exists it will be overwritten.\nDefaults to /tmp/tron_socket', default="/tmp/tron_socket")
args = parser.parse_args()

tronserver.TronGame().start(args.socket)
