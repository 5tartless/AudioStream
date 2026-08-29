from backend.agents.base import Agent
from backend.audio.playback import AudioListener
from backend import CURRENT_MENU, CURRENT_CONFIG
import socket

class Client(Agent):
    def __init__(self):
        super().__init__()
        self.audio_manager: AudioListener = AudioListener()
        # self.net_stats: dict = {} #unused
        self.server_ip: str = "192.168.100.66" #hardcoded

    def gen_threads(self):
        return super().gen_threads(lambda agent: self.deactivate(from_server=True, agent=agent))

    def activate(self):
        try:
            self.resock(reuseaddr=False)
            self.sock.settimeout(3.0)
            self.sock.connect((self.server_ip, CURRENT_CONFIG.CLIENT_PORT))
            
            super().activate()
            self.audio_manager.listen(self.io_device)
        except socket.timeout:
            print("(!) Connection timeout! Check internet.")
        except ConnectionRefusedError:
            print("(!) Couldn't reach server. Server may be offline.")

    def deactivate(self, from_server: bool = False, agent: any = None, *args, **kwargs):
        if not from_server:
            self.sock.shutdown(socket.SHUT_WR)
        else:
            self.active = False
            CURRENT_MENU.refresh()
        if agent: self.agent_manager.remove_agent(agent)
        return super().deactivate()
