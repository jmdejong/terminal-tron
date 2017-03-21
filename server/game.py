

import random

class Ground:
    
    field = []
    #ground = []
    width = 0
    height = 0
    
    def __init__(self):
        
        self.field = {}
    
    def get(self, x, y):
        if (x, y) not in self.field:
            self.field[(x,y)] = GroundPatch()
        return self.field[(x, y)]
    
    def addObj(self, x, y, obj):
        p = self.get(x, y).addObj(obj)
        
    def removeObj(self, x, y, obj):
        self.get(x, y).removeObj(obj)


    
class GroundPatch:
    
    height = 0
    size = 0
    char = ' '
    objects = None
    
    def __init__(self, height=0, objects=None):
        self.height = height
        # objects is actually a set, but because its elements are mutable
        # it is implemented as a dictionary with the id as index
        self.objects = objects or {}
        #self.char = random.choice('.,"\'`')
    
    def accesible(self):
        return not any(obj.solid for obj in self.objects.values())
    
    def addObj(self, obj):
        self.objects[id(obj)] = obj
    
    def removeObj(self, obj):
        if id(obj) in self.objects:
            del self.objects[id(obj)]
    
    def getObjs(self):
        return self.objects.values()
    
    def getTopObj(self):
        topObj = self
        for obj in self.getObjs():
            if obj.size > topObj.size:
                topObj = obj
        return topObj
        

class Wall:
    
    char = '#'
    solid = True
    size = 1
    


class Player:
    
    x = 0
    y = 0
    name = "gronald"
    char = '@'
    size = 2
    direction = None
    solid = False
    
    def __init__(self, x, y, field, game, name=None):
        self.controller = {}
        self.game = game
        self.name = name or str(id(self))
        self.char = self.name[0]
        self.x = x
        self.y = y
        self.field = field
        self.place(x, y)
        #self.direction = random.choice(["north", "south", "east", "west"])
    
    def getControlInterface(self):
        return self.controller
    
    def place(self, x, y):
        if self.field:
            self.field.removeObj(self.x, self.y, self)
            self.field.addObj(x, y, self)
        self.x = x
        self.y = y
            
    
    def update(self):
        
        #dx = bool("east" in self.controller and self.controller["east"]) - bool("west" in self.controller and self.controller["west"])
        #dy = bool("south" in self.controller and self.controller["south"]) - bool("north" in self.controller and self.controller["north"])
        
        if "move" in self.controller:
            direction = self.controller["move"]
            if not self.direction or direction in {"north","south"} and self.direction in {"east","west"} or self.direction in {"north","south"} and direction in {"east","west"}:
                self.direction = self.controller["move"]
        if self.direction not in {"north", "south", "east", "west"}:
            self.direction = random.choice(["north", "south", "east", "west"])
        #self.controller.clear()
        dx = (self.direction == "east") - (self.direction == "west")
        dy = (self.direction == "south") - (self.direction == "north")
        
        self.field.addObj(self.x, self.y, Wall())
        self.place(self.x + dx, self.y + dy)
            
        if not self.field.get(self.x, self.y).accesible():
            self.die()
    
    def die(self):
        self.game.removePlayer(self.name)
        self.game.deaths += 1
        





class Game:
    
    field = None
    width = 0
    height = 0
    deaths = 0
    
    def __init__(self, width, height):
        self.players = {}
        self.field = Ground()
        self.width = width
        self.height = height
        for x in range(width):
            self.field.addObj(x, 0, Wall())
            self.field.addObj(x, height-1, Wall())
        for y in range(1,height-1):
            self.field.addObj(0, y, Wall())
            self.field.addObj(width-1, y, Wall())
    
    def makePlayer(self,name=None, x=None, y=None ):
        #logging.debug("%s, %s"%(x,y))
        if (name in self.players):
            raise Exception("A player with that name already exists")
        if x == None:
            x = random.randint(5, self.width-5)
        if y == None:
            y = random.randint(5, self.height-5)
        p = Player(x, y, self.field, self, name)
        self.players[p.name] = p
        return p.getControlInterface()
    
    def removePlayer(self, name):
        if name in self.players:
            player = self.players[name]
            self.field.removeObj(player.x, player.y, player)
            del self.players[name]
    
    def countPlayers(self):
        return len(self.players)
    
    def getController(self, name):
        return self.players[name].getControlInterface()
    
    def update(self):
        self.deaths = 0
        for player in frozenset(self.players.values()):
            player.update()
