from backend.agents.base import Agent
from backend.audio.capture import AudioCapturer
from backend.audio.audio_sender.udp import UDPSender
from backend import CURRENT_MENU, CURRENT_CONFIG
import socket, threading, time

class Server(Agent):
    def __init__(self):
        super().__init__()
        self.name: str = "debug"
        self.audio_manager: AudioCapturer = AudioCapturer(server=self)
        self.discover_thread: threading.Thread = None

    def _on_agent_added(self, agent):
        super()._on_agent_added(agent)
        if len(self.agent_manager.get_agents()) == 1:
            self.audio_manager.stream(self.io_device)
        CURRENT_MENU.refresh()
    def _on_agent_removed(self, *args):
        super()._on_agent_removed(*args)
        if self.agent_manager.empty():
            self.audio_manager.running = False
        CURRENT_MENU.refresh()

    def push_clients(self, data: any) -> None:
        for sender in self.senders:
            sender.send_all(
                data=data,
                targets=self.agent_manager.pull_agents(_type=type(sender))()
            )

    def gen_threads(self, all: bool = True):
        if all: self.discover_thread = threading.Thread(target=self._discover, daemon=True)
        return super().gen_threads(on_udp_cw_disconnect=self.agent_manager.remove_agent)

    def activate(self):
        self.resock(reuseaddr=True)
        try:
            self.sock.bind(("0.0.0.0", CURRENT_CONFIG.SERVER_PORT))
            self.sock.settimeout(1.0)
            self.sock.listen(1)
        except OSError:
            print(f"(!) Another server is already using: {CURRENT_CONFIG.SERVER_PORT}")
            return
        super().activate()
        self.discover_thread.start()

    def deactivate(self):
        self.active = False
        self.audio_manager.running = False
        self.discover_thread.join()
        super().deactivate()

    def _discover(self):
        while self.active:
            try:
                client_sock, client_address = self.sock.accept()
                client_ip = client_address[0]
                
                refused: bool = False
                for client in self.agent_manager.pull_agents(_type=UDPSender)():
                    if client.ip == client_ip:
                        refused = True
                        client_sock.sendall(b"(!) You are already connected to this server, try again later.")
                        client_sock.close()
                        break
                if refused: continue
            except socket.timeout:
                continue

            self.agent_manager.add_agent(UDPSender, client_ip, {"socket": client_sock})