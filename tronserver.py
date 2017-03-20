#! /usr/bin/python3



import time
import json
from game import Game
from drawfield import DrawField
import server
import argparse


WIDTH = 40
HEIGHT = 25



class PlayerConnection:
    
    name = ""
    initialized = False
    data = ""
    


class TronGame:
    
    def __init__(self):
        
        #self.buff = Buffer()
        self.serv = server.Server(self.newConnection, self.receive, self.close)
        
        self.connections = {}
        
        self.scores = {}
        
    def start(self, address="/tmp/tron_socket"):
        self.serv.start(address)
        
        while True:
            self.game_round()
        
        
    
    def game_round(self):
        self.game = Game(WIDTH, HEIGHT)
        for player in self.connections.values():
            self.game.makePlayer(player.name)
        readydate = time.time()
        while True:
            
            for name, command in self.getInput().items():
                if name not in self.game.players:
                    self.game.makePlayer(name)
                
            if not self.game.countPlayers():
                readydate = time.time()
            if time.time() - readydate > 4.0:
                break
            
            self.sendState()
            time.sleep(0.2)
        
        self.game_loop()
        
        endTime = time.time()
        while time.time() - endTime < 4.0:
            self.sendState()
            time.sleep(0.2)
    
    def game_loop(self):
        
        keepRunning = True
        while keepRunning:
            
            self.update()
            keepRunning = self.game.countPlayers() > 0
            time.sleep(0.2)
    
    def update(self):
    
        commands = self.getInput()
        #self.flushInput()
        for player, command in commands.items():
            
            if command and player in self.game.players:
                controller = self.game.getController(player)
                
                #validCommands = list(set(command) & {"north", "south", "east", "west"})
                
                controller["move"] =  command if command in {"north", "south", "east", "west"} else ""
        
        self.game.update()
        
        self.sendState()
    
    def sendState(self):
        
        output = DrawField(self.game.field, 0, 0, WIDTH, HEIGHT).toString()
        
        data = {
            "type": "update",
            "field": output,
            "width": WIDTH,
            "height": HEIGHT
        }
        
        self.serv.broadcast(bytes(json.dumps(data), 'utf-8'))
    
    def newConnection(self, n):
        self.connections[n] = PlayerConnection()
    
    def receive(self, n, data):
        data = data.decode('utf-8')
        c = self.connections[n]
        if not c.initialized:
            
            c.name = data
            c.initialized = True
            print("new player: "+c.name)
        else:
            c.data = data
    
    def getInput(self):
        # return a dict of players and the commands since flushInput was called
        return {p.name: p.data for p in self.connections.values() if p.initialized}
    
    def close(self, connection):
        if self.game and self.connections[connection]:
            print("player "+self.connections[connection].name+" left")
            self.game.removePlayer(self.connections[connection].name)
            del self.connections[connection]
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', help='The socket file to listen to. Use this is the default socket exists already. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    TronGame().start(args.socket)
