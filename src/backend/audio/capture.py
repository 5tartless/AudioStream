from contextlib import ExitStack
from backend import CURRENT_MENU, CURRENT_CONFIG
from backend.audio.base import AudioManager
import soundcard as sc, threading, time, struct

class AudioCapturer(AudioManager):
    def __init__(self, server, channels = 2):
        super().__init__(channels)
        self.server = server #reference
        
    def speaker_recorder(self, speaker) -> any:
        return sc.get_microphone(id=speaker.name, include_loopback=True)

    def stream(self, input_device: any) -> None:
        self.running = True
        input_device = self.to_sc_device(input_device)

        stream_thread = threading.Thread(
            target=self._stream_thread,
            args=(input_device,),
            daemon=True
        )
        stream_thread.start()
        CURRENT_MENU.refresh()

    def _stream_thread(self, input_device: any) -> None:
        with ExitStack() as stack:
            if type(input_device).__name__ == "_Speaker":
                input_device = self.speaker_recorder(input_device)
            ctx = self._create_device(input_device, samplerate=CURRENT_CONFIG.SERVER_SAMPLE_RATE, blocksize=CURRENT_CONFIG.SERVER_BLOCK_SIZE)
            input = None
            # packet_id = 0
            while self.running:
                # packet_id += 1
                # payload = struct.pack("<Id", packet_id, time.perf_counter()) + data.tobytes()
                if not self.server.agent_manager.empty():
                    if not input:
                        input = stack.enter_context(ctx)
                    data = input.record(numframes=CURRENT_CONFIG.SERVER_BLOCK_SIZE)
                    self.server.push_clients(data.tobytes())
        self.stop()
