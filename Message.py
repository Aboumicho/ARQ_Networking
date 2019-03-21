class Message:
    def __init__(self):
        self.message = ""

    def append(self, payload):
        self.message += payload 