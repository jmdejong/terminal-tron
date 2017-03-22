#! /usr/bin/python3

import sys

if sys.version_info[0] < 3:
    print("This game is written in python 3.\nRun 'python3 "+sys.argv[0]+"' or './"+sys.argv[0]+"'")
    sys.exit(-1)

sys.path.append("./client/")
sys.path.append("./shared/")

import argparse
import getpass
import client


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', help='Your player name (must be unique!). Defaults to username', default=getpass.getuser())
parser.add_argument('-s', '--socket', help='The socket file to connect to. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
parser.add_argument('-p', '--spectate', help='Join as spectator', action="store_true")
args = parser.parse_args()

client.main(args.name, args.socket, args.spectate)
