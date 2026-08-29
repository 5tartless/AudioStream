from backend.audio.base import AudioManager
from backend.audio.audio_sender.base import Sender
from backend.audio.audio_sender.udp import UDPSender
from backend.network.agent_manager import AgentData, AgentManager
from backend.network.udp_watcher import UDPWatcher
import socket

class Agent():
    def __init__(self):
        self.sock: socket.socket = None
        self.active: bool = False
        self.io_device: any = None
        self.audio_manager: AudioManager = None

        self.agent_manager: AgentManager = AgentManager(
            on_agent_added=self._on_agent_added,
            on_agent_removed=self._on_agent_removed
        )
        self.senders: list[Sender] = []
        self.connection_watchers: list = []

    def _on_agent_added(self, agent: AgentData): 
        found: bool = False
        if self.senders:
            for instance in self.senders:
                if isinstance(instance, agent._type):
                    found = True
                    break
        if not found:
            self.senders.append(agent._type())
    def _on_agent_removed(self, *args): pass

    def _cut_cw_connections(self):
        for cw in self.connection_watchers:
            cw.kill_all()
    def _activate_cw(self):
        for cw in self.connection_watchers:
            cw.start()
    def _deactivate_cw(self):
        for cw in self.connection_watchers:
            cw.stop()

    def gen_threads(self, on_udp_cw_disconnect: any):
        self.connection_watchers.clear()
        self.connection_watchers.append(UDPWatcher(self.agent_manager.pull_agents(UDPSender), on_udp_cw_disconnect))

    def resock(self, reuseaddr: bool) -> socket.socket:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if reuseaddr: 
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return self.sock

    def toggle_status(self):
        {True: self.deactivate, False: self.activate}[self.active]()

    #activate and deactivate should not be called alone, instead use self.toggle_status
    def activate(self):
        self.active = True
        self.gen_threads()
        self._activate_cw()

    def deactivate(self):
        self.active = False

        self.sock.close()
        self.audio_manager.running = False

        self._cut_cw_connections()
        self._deactivate_cw()

        self.gen_threads()
        for sender in self.senders:
            sender.close()
        self.senders.clear()