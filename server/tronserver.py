#! /usr/bin/python3



import time
import json
from game import Game
from drawfield import DrawField
import server
import argparse
import threading


WIDTH = 60
HEIGHT = 30



class PlayerConnection:
    
    name = ""
    initialized = False
    data = ""
    score = 0 # todo: store this somewhere else

#class Player:
    
    #def __init__(self, name, connection):
        #self.score = 0
        #self.name = name
        #self.connection = connection
    
    #def isConnected(self):
        #return self.connection.initialized

class TronGame:
    
    def __init__(self):
        
        self.serv = server.Server(self.newConnection, self.receive, self.close)
        
        self.connections = {}
        self.players = {}
        
    def start(self, address="/tmp/tron_socket"):
        
        self.cv = threading.Condition()
        
        self.serv.start(address)
        
        while True:
            self.game_round()
        
        
    
    def game_round(self):
        self.game = Game(WIDTH, HEIGHT)
        for player in self.connections.values():
            self.game.makePlayer(player.name)
        
        self.lobby_loop()
        
        self.game_loop()
        
        endTime = time.time()
        while time.time() - endTime < 4.0:
            self.sendState()
            time.sleep(0.2)
    
    def lobby_loop(self):
        
        readydate = time.time()
        while True:
            
            for c in self.connections.values():
                command = c.data
                name = c.name
                if name not in self.game.players:
                    self.game.makePlayer(name)
                
            if not self.game.countPlayers():
                with self.cv:
                    self.cv.wait()
                readydate = time.time()
            if time.time() - readydate > 4.0:
                break
            
            self.sendState()
            time.sleep(0.2)
    
    
    def game_loop(self):
        
        keepRunning = True
        while keepRunning:
            
            self.update()
            keepRunning = self.game.countPlayers() > 0
            time.sleep(0.2)
    
    def update(self):
        
        for c in self.connections.values():
            command = c.data
            player = c.name
            if command and player in self.game.players:
                controller = self.game.getController(player)
                controller["move"] = command if command in {"north", "south", "east", "west"} else ""
        
        lastCount = self.game.countPlayers()
        self.game.update()
        if self.game.deaths:
            for c in self.connections.values():
                if c.name in self.game.players:
                    c.score += 1
        
        self.sendState()
    
    def sendState(self):
        
        output = DrawField(self.game.field, 0, 0, WIDTH, HEIGHT).toString()
        
        data = {
            "type": "update",
            "field": output,
            "width": WIDTH,
            "height": HEIGHT,
            "players": {c.name: c.score for c in self.connections.values() if c.initialized}
        }
        
        self.serv.broadcast(bytes(json.dumps(data), 'utf-8'))
    
    def newConnection(self, n):
        self.connections[n] = PlayerConnection()
        with self.cv:
            self.cv.notify()
    
    def receive(self, n, data):
        data = json.loads(data.decode('utf-8'))
        c = self.connections[n]
        if "name" in data:
            name = data["name"]
            if name in self.getNames():
                self.serv.send(n, bytes(json.dumps({"error":"nametaken"}), "utf-8"))
            else:
                c.name = name
                c.initialized = True
                #if c.name in self.players:
                    #self.players[name].connection = n
                #else:
                    #self.players[name] = Player(name, n)
                print("new player: "+c.name)
        if "input" in data:
            c.data = data["input"]
    
    
    def getNames(self):
        return {p.name for p in self.connections.values()}
    
    def close(self, connection):
        if connection in self.connections:
            name = self.connections[connection].name
            del self.connections[connection]
            if self.game:
                self.game.removePlayer(name)
            print("player "+name+" left")
            #self.connections[connection].initialized = False
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', help='The socket file to listen to. Use this if the default socket exists already.\nWARNING: if the given file exists it will be overwritten.\nDefaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    TronGame().start(args.socket)
