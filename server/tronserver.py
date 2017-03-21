#! /usr/bin/python3



import json
import server


class PlayerConnection:
    
    name = ""
    initialized = False
    data = ""
    score = 0 # todo: store this somewhere else


class TronServer:
    
    
    def __init__(self, game):
        
        self.serv = server.Server(self.newConnection, self.receive, self.close)
        self.connections = {}
        
        self.game = game
    
    def start(self, address):
        self.serv.start(address)
    
    def sendState(self, field, players, width, height):
        
        data = {
            "type": "update",
            "field": field,
            "width": width,
            "height": height,
            "players": players
        }
        self.serv.broadcast(bytes(json.dumps(data), 'utf-8'))
    
    def newConnection(self, n):
        self.connections[n] = PlayerConnection()
        with self.game.cv:
            self.game.cv.notify()
    
    def receive(self, n, data):
        data = json.loads(data.decode('utf-8'))
        c = self.connections[n]
        if "name" in data:
            name = data["name"]
            if name in self.game.players:
                self.serv.send(n, bytes(json.dumps({"error":"nametaken"}), "utf-8"))
            else:
                c.name = name
                c.initialized = True
                self.game.players[name] = c
                print("new player: "+name)
        if "input" in data:
            c.data = data["input"]
    
    def close(self, connection):
        if connection in self.connections:
            name = self.connections[connection].name
            del self.connections[connection]
            if name in self.game.players:
                del self.game.players[name]
            if self.game.game:
                self.game.game.removePlayer(name)
            print("player "+name+" left")
    
