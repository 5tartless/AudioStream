class Sender():
    def __init__(self, bridge: any):
        self.bridge: any = bridge
        self._targets: list = []

    def set_targets(self, targets):
        self._targets = targets
        
    def send_all(self, bridge):
        pass
    def close(self):
        pass