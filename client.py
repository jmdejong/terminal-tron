#! /usr/bin/python3

import sys

if sys.version_info[0] < 3:
    print("This game is written in python 3.\nRun 'python3 client.py' or './client.py'")

import curses
import socket
import threading
#import logging
import varmsglen
import json
import getpass
import argparse

#logging.basicConfig(filename="client.log", filemode='w', level=logging.DEBUG)



class Connection:
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    def connect(self, address):
        self.sock.connect(address)
    
    def listen(self, callback, onError):
        while True:
            try:
                data = varmsglen.receive(self.sock)
            except Exception as err:
                onError(err)
            callback(data)
    
    def send(self, message):
        varmsglen.send(self.sock, bytes(message, 'utf-8'))



class Screen:
    
    
    def __init__(self, stdscr):
        curses.curs_set(0)
        self.height, self.width = stdscr.getmaxyx()
        self.stdscr = stdscr
        self.fieldpad = curses.newpad(100,200)
        self.playerpad = curses.newpad(100,100)
    
    
    def put(self, field):
        self.fieldpad.clear()
        self.fieldpad.addstr(0, 0, field)
        self.height, self.width = self.stdscr.getmaxyx()
        self.fieldpad.refresh(0,0,0,0,self.height-1,self.width-1)
        
    def putPlayers(self, players, x=0, y=0):
        self.playerpad.clear()
        self.playerpad.addstr(0, 0, players)
        self.height, self.width = self.stdscr.getmaxyx()
        #print(x, y, self.width, self.height)
        if x < self.width and y < self.height:
            self.playerpad.refresh(0,0,y,x,self.height-1,self.width-1)


class Client:
    
    def __init__(self, stdscr, name="___", address="/tmp/tron_socket"):
        self.stdscr = stdscr
        self.screen = Screen(stdscr)
        
        self.name = name
        
        self.keepalive = True
        
        self.connection = Connection()
        self.connection.connect(address)
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
    
    def update(self, data):
        if not self.keepalive:
            sys.exit()
        data = json.loads(data.decode('utf-8'))
        if 'error' in data:
            if data['error'] == "nametaken":
                print("error: name is already taken", file=sys.stderr)
                self.close()
        if 'field' in data:
            self.screen.put(data['field'])
        if 'players' in data:
            players = [(score, name) for name, score in data['players'].items()]
            players.sort(key=lambda p: -p[0])
            self.screen.putPlayers('\n'.join("%4d %s" % p for p in players), self.fieldWidth)
        if 'width' in data:
            self.fieldWidth = data['width']
        if 'height' in data:
            self.fieldHeight = data['height']
    
    def command_loop(self):
        
        commands = {"w": "north", "s": "south", "d": "east", "a": "west"}
        
        while self.keepalive:
            key = self.stdscr.getch()
            if key == ord('q'):
                self.keepalive = False
            if chr(key) in commands:
                self.connection.send(json.dumps({"input":commands[chr(key)]}))


def main(stdscr):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='Your player name (must be unique!). Defaults to username', default=getpass.getuser())
    parser.add_argument('-s', '--socket', help='The socket file to connect to. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    
    #name = getpass.getuser()
    client = Client(stdscr, args.name, args.socket)
    


curses.wrapper(main)
