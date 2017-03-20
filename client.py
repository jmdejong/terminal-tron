#! /usr/bin/python3

import curses
import socket
import sys
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
        height, width = stdscr.getmaxyx()
        self.stdscr = stdscr
    
    
    def put(self, string, x=0, y=0):
        self.stdscr.addstr(y, x, string)
        self.stdscr.refresh()


class Client:
    
    def __init__(self, stdscr, name="___", address="/tmp/tron_socket"):
        self.stdscr = stdscr
        self.screen = Screen(stdscr)
        
        self.name = name
        
        self.keepalive = True
        
        self.connection = Connection()
        self.connection.connect(address)
        self.connection.send(name)
        
        threading.Thread(target=self.command_loop).start()
        self.connection.listen(self.update, self.close)
    
    def listen(self):
        self.connection.listen(self.update)
    
    def close(self, err):
        self.keepalive = False
        sys.exit()
    
    def update(self, data):
        if not self.keepalive:
            sys.exit()
        data = json.loads(data.decode('utf-8'))
        self.screen.put(data['field'])
    
    def command_loop(self):
        
        commands = {"w": "north", "s": "south", "d": "east", "a": "west"}
        
        while self.keepalive:
            key = self.stdscr.getch()
            if key == ord('q'):
                self.keepalive = False
            if chr(key) in commands:
                self.connection.send(commands[chr(key)])


def main(stdscr):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='Your player name (must be unique!). Defaults to username', default=getpass.getuser())
    parser.add_argument('-s', '--socket', help='The socket file to connect to. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    
    #name = getpass.getuser()
    client = Client(stdscr, args.name, args.socket)
    


curses.wrapper(main)
