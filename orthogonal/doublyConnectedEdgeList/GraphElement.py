

class GraphElement:
    def __init__(self, name):
        self.id = name

    def __hash__(self):
        return hash(self.id)
