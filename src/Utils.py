# Simple stack class with elementary functions to use
class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

class Queue:
    def __init__(self):
        self.list = []
    
    def isEmpty(self):
        return len(self.list) == 0

    def push(self,item):
        self.list.insert(0,item)

    def pop(self):
        return self.list.pop()

  