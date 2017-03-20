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
    active = False
    data = ""
    score = 0 # todo: store this somewhere else

#class Player:
    
    #def __init__(self, name, connection):
        #self.score = 0
        #self.name = name
        #self.connection = connection
    
    #def isConnected(self):
        #return self.connection.active

class TronGame:
    
    def __init__(self):
        
        self.serv = server.Server(self.newConnection, self.receive, self.close)
        
        self.connections = {}
        self.players = {}
        
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
            
            for c in self.connections.values():
                command = c.data
                name = c.name
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
        
        for c in self.connections.values():
            command = c.data
            player = c.name
            if command and player in self.game.players:
                controller = self.game.getController(player)
                controller["move"] = command if command in {"north", "south", "east", "west"} else ""
        
        lastCount = self.game.countPlayers()
        self.game.update()
        if self.game.countPlayers() < lastCount:
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
            "players": {c.name: c.score for c in self.connections.values() if c.active}
        }
        
        self.serv.broadcast(bytes(json.dumps(data), 'utf-8'))
    
    def newConnection(self, n):
        self.connections[n] = PlayerConnection()
    
    def receive(self, n, data):
        data = json.loads(data.decode('utf-8'))
        c = self.connections[n]
        if "name" in data:
            name = data["name"]
            if name in self.getNames():
                self.serv.send(n, bytes(json.dumps({"error":"nametaken"}), "utf-8"))
            else:
                c.name = name
                c.active = True
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
        if self.game and connection in self.connections:
            self.game.removePlayer(self.connections[connection].name)
            print("player "+self.connections[connection].name+" left")
            #self.connections[connection].active = False
            del self.connections[connection]
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', help='The socket file to listen to. Use this if the default socket exists already. Defaults to /tmp/tron_socket', default="/tmp/tron_socket")
    args = parser.parse_args()
    
    TronGame().start(args.socket)
