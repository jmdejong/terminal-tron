

import tronserver
from game import Game
from drawfield import DrawField
import argparse
import threading
import time
import os
import signal
import sys

WIDTH = 60
HEIGHT = 30


class TronGame:
    
    def __init__(self):
        
        self.server = tronserver.TronServer(self)
        self.players = {}
        
    def start(self, address="/tmp/tron_socket"):
        
        
        
        def cleanup(*args):
            print(args)
            print("cleaning")
            try:
                os.unlink(address)
            except FileNotFoundError:
                if os.path.exists(address):
                    raise
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, cleanup)
        
        self.cv = threading.Condition()
        
        self.server.start(address)
        try:
            while True:
                self.game_round()
        except Exception:
            raise
        finally:
            try:
                os.unlink(address)
            except FileNotFoundError:
                print("catching")
                if os.path.exists(address):
                    raise
        
        
    
    def game_round(self):
        self.game = Game(WIDTH, HEIGHT)
        for name in self.players:
            self.game.makePlayer(name)
        
        self.lobby_loop()
        
        self.game_loop()
        
        endTime = time.time()
        while time.time() - endTime < 4.0:
            self.sendState()
            time.sleep(0.2)
    
    def lobby_loop(self):
        
        self.sendState()
        readydate = time.time()
        while True:
            
            for c in self.players.values():
                command = c.data
                name = c.name
                if name not in self.game.players:
                    self.game.makePlayer(name)
                
            self.sendState()
            
            if not len(self.players):
                with self.cv:
                    print("sleeping")
                    self.cv.wait()
                    print("awake!")
                readydate = time.time()
            if time.time() - readydate > 4.0:
                break
            
            time.sleep(0.2)
    
    
    def game_loop(self):
        
        keepRunning = True
        while keepRunning:
            
            self.update()
            keepRunning = self.game.countPlayers() > 0
            time.sleep(0.2)
    
    def update(self):
        
        for c in self.players.values():
            command = c.data
            player = c.name
            if command and player in self.game.players:
                controller = self.game.getController(player)
                controller["move"] = command if command in {"north", "south", "east", "west"} else ""
        
        lastCount = self.game.countPlayers()
        self.game.update()
        if self.game.deaths:
            for name in self.game.players:
                self.players[name].score += 1
        
        self.sendState()
    
    def sendState(self):
        
        output = DrawField(self.game.field, 0, 0, WIDTH, HEIGHT).toString()
        
        self.server.sendState(output, {c.name: c.score for c in self.players.values()}, WIDTH, HEIGHT)
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', help='The socket file to listen to. Use this if the default socket exists already.\nWARNING: if the given file exists it will be overwritten.\nDefaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    TronGame().start(args.socket)
