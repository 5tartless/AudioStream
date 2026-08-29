from backend.network.watcher import ConnectionWatcher
from socket import timeout, error

class UDPWatcher(ConnectionWatcher):
    def __init__(self, agents, on_disconnect):
        super().__init__(agents, on_disconnect)
        self.agents.on_set = self.set_timeout
    
    def set_timeout(self) -> None:
        for agent in self.agents():
            agent.bridge["socket"].settimeout(2.5)

    def _disconnect(self, agent):
        self.on_disconnect(agent)
        agent.bridge["socket"].close()
        self.agents.set()

    def kill_all(self):
        return super().kill_all(self._disconnect)

    def _watch(self):
        self.set_timeout()
        while self.running:
            for agent in self.agents():
                agent_socket = agent.bridge["socket"]
                try:
                    dummy_data = agent_socket.recv(1024)
                    if not dummy_data:
                        self._disconnect(agent)
                    else:
                        print(dummy_data)
                except timeout:
                    pass
                except error:
                    self._disconnect(agent)

        return super()._watch()