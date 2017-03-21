        

class DrawField:
    
    field = []
    width = 0
    height = 0
    
    def __init__(self, field, xmin=0, ymin=0, width=0, height=0, filler = ' '):
        self.width = width or field.width - xmin
        self.height = height or field.height - ymin
        self.field = [filler]*width*height
        self.filler = filler
        
        for x in range(xmin, xmin+self.width):
            for y in range(ymin, ymin+self.height):
                #if field.isValid(x,y):
                    self.field[x + y*width] = field.get(x,y).getTopObj().char
    
    def toString(self, separator="", lineseparator = '\n'):
        
        s = ""
        for i, val in enumerate(self.field):
            s += val if len(val) else self.filler
            if (i+1)%self.width:
                s += separator
            elif i+1 != self.width * self.height:
                s += lineseparator
        return s
