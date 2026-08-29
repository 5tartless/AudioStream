from backend.audio.audio_sender.base import Sender
from backend.network.agent_manager import AgentData
from backend import CURRENT_CONFIG
import socket, time

class UDPSender(Sender):
    def __init__(self):
        super().__init__(bridge=socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    def send_all(self, data: bytes, targets: list[AgentData]):
        if self.bridge and targets:
            for target in targets:
                self.bridge.sendto(data, (target.ip, CURRENT_CONFIG.SERVER_STREAM_PORT))
            return super().send_all(self.bridge)

    def close(self) -> None:
        self.bridge.close()
        return super().close()