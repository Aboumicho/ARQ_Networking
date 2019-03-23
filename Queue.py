class Queue:

    def __init__(self):
        self.list = []
        self.size = 0

    def add(self, packet):
        self.list.append(packet)

    def remove(self):
        if(len(self.list)>0):
            self.list.pop()

    def setSize(self, n):
        self.size = n
        
    def reset(self):
        self.list = []