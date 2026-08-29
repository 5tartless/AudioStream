from backend import CURRENT_MENU
import socket, soundcard as sc

class AudioManager():
    def __init__(self, channels: int = 2):
        self.CHANNELS = channels
        self.sock: socket.socket = None
        self.running: bool = False
    
    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        CURRENT_MENU().wait_time = 1

    def to_sc_device(self, audio_device: any) -> any:
        if type(audio_device).__name__ == "AudioDevice":
            if audio_device.type == "input":
                return sc.get_microphone(id=audio_device.name)
            elif audio_device.type == "output":
                return sc.get_speaker(id=audio_device.name)
        return audio_device
    
    def _create_device(self, device, samplerate: int, blocksize: int):
        if device:
            if type(device).__name__ == "_Speaker":
                return device.player(samplerate=samplerate, blocksize=blocksize)
            elif type(device).__name__ == "_Microphone":
                return device.recorder(samplerate=samplerate, blocksize=blocksize)
        return None