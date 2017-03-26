#! /usr/bin/python3

import sys

import curses
import threading
#import logging
import json
import getpass
import argparse
from connection import Connection
from screen import Screen

#logging.basicConfig(filename="client.log", filemode='w', level=logging.DEBUG)


class Client:
    
    def __init__(self, stdscr, name="___", address="/tmp/tron_socket", spectate=False):
        self.stdscr = stdscr
        self.screen = Screen(stdscr)
        
        self.name = name
        
        self.keepalive = True
        
        self.connection = Connection()
        self.connection.connect(address)
        if not spectate:
            self.connection.send(json.dumps({"name":name}))
        
        self.fieldWidth = 0
        self.fieldHeight = 0
        
        threading.Thread(target=self.listen, daemon=True).start()
        self.command_loop()
    
    def listen(self):
        self.connection.listen(self.update, self.close)
    
    def close(self, err=None):
        self.keepalive = False
        sys.exit()
    
    def update(self, databytes):
        if not self.keepalive:
            sys.exit()
        datastr = databytes.decode('utf-8')
        data = json.loads(datastr)
        if 'error' in data:
            if data['error'] == "nametaken":
                print("error: name is already taken", file=sys.stderr)
                self.close()
        if 'field' in data:
            self.screen.put(data['field'])
        if 'players' in data and len(data['players']):
            players = [(score, name) for name, score in data['players'].items()]
            players.sort(key=lambda p: -p[0])
            self.screen.putPlayers('\n'.join("%4d %s" % p for p in players), self.fieldWidth)
        if 'width' in data:
            self.fieldWidth = data['width']
        if 'height' in data:
            self.fieldHeight = data['height']
        self.screen.refresh()
    
    def command_loop(self):
        
        commands = {
            ord("w"): "north",
            curses.KEY_UP: "north",
            ord("s"): "south",
            curses.KEY_DOWN: "south",
            ord("d"): "east",
            curses.KEY_RIGHT: "east",
            ord("a"): "west",
            curses.KEY_LEFT: "west"
        }
        
        while self.keepalive:
            key = self.stdscr.getch()
            if key == ord('q'):
                self.keepalive = False
            if key in commands:
                self.connection.send(json.dumps({"input":commands[key]}))


def main(name, socket, spectate=False):
    
    
    def start(stdscr):
        client = Client(stdscr, name, socket, spectate)
    
    curses.wrapper(start)
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='Your player name (must be unique!). Defaults to username', default=getpass.getuser())
    parser.add_argument('-s', '--socket', help='The socket file to connect to. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
    parser.add_argument('-p', '--spectate', help='Join as spectator', action="store_true")
    args = parser.parse_args()
    
    main(args.name, args.socket, args.spectate)
    

