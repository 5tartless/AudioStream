from backend import CURRENT_MENU, CURRENT_CONFIG
from backend.audio.base import AudioManager
from math import ceil
import socket, numpy, queue, threading, time

class AudioListener(AudioManager):
    def __init__(self, desired_target_ms: int = 23, allowed_jitter_ms: int = 12, channels: int = 2):
        super().__init__(channels)
        self.desired_target_ms: int = desired_target_ms
        self.allowed_jitter_ms: int = allowed_jitter_ms
        self.BUFFER_TARGET: int = ceil(self.desired_target_ms / self._get_block_duration_ms())
        self.QUEUE_THRESHOLD: int = self.BUFFER_TARGET + self._get_headroom_blocks() + 4
        self.queue: queue.Queue = None

        #stats
        self.packets_received = 0
        self.packets_dropped = 0
        self.buffer_underflows = 0
        self.last_packet_time = None
        self.jitters = []
        self.stats_summary: str = None

        self.elapsed = 0

    def _get_block_duration_ms(self) -> float:
        return (CURRENT_CONFIG.CLIENT_BLOCK_SIZE / CURRENT_CONFIG.CLIENT_SAMPLE_RATE) * 1000
    def _get_headroom_blocks(self) -> int:
        return ceil(self.allowed_jitter_ms / self._get_block_duration_ms())
    def _get_queue_max_size(self) -> int:
        return self.QUEUE_THRESHOLD + 4

    def listen(self, playback_on: any):
        playback_on = self.to_sc_device(playback_on)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", CURRENT_CONFIG.CLIENT_LISTEN_PORT))
        self.running = True
        self.queue = queue.Queue(maxsize=self._get_queue_max_size()+3)
        
        network_thread = threading.Thread(target=self._network_thread, daemon=True)
        playback_thread = threading.Thread(target=self._playback_thread, kwargs={'playback_on': playback_on}, daemon=True)
        stats_thread = threading.Thread(target=self._stats_thread, daemon=True)

        network_thread.start()
        playback_thread.start()
        stats_thread.start()

    def _network_thread(self):
        # INFO GIVEN FROM GEMINI
        # Calculate the exact byte size of one audio block
        # Soundcard uses float32 (4 bytes per sample) * block_size * channels
        # 4 bytes * 128 * 2 = 1024 bytes
        expected_bytes = 4 * CURRENT_CONFIG.CLIENT_BLOCK_SIZE * self.CHANNELS

        while self.running:
            try:
                packet, _ = self.sock.recvfrom(expected_bytes)
                if self.last_packet_time:
                    arrival_delta = time.time() - self.last_packet_time
                    ideal_delta = CURRENT_CONFIG.CLIENT_BLOCK_SIZE / CURRENT_CONFIG.CLIENT_SAMPLE_RATE
                    self.jitters.append(abs(arrival_delta - ideal_delta))
                self.last_packet_time = time.time()
                self.packets_received += 1
                    
                # if desync then clear all the queue
                # if self.queue.qsize() >= self.QUEUE_THRESHOLD:
                #     while not self.queue.empty():
                #         try:
                #             self.queue.get_nowait()
                #             self.packets_dropped += 1
                #         except queue.Empty:
                #             break

                try:
                    self.queue.put_nowait(packet)
                except queue.Full:
                    self.packets_dropped += 1
                    try: 
                        self.queue.get_nowait()
                    except queue.Empty:
                        pass
                    finally:
                        self.queue.put_nowait(packet)
            except socket.error:
                break
        self.stop()

    def _playback_thread(self, playback_on: any):
        with playback_on.player(samplerate=CURRENT_CONFIG.CLIENT_SAMPLE_RATE) as output:
            while self.running:
                if self.queue.qsize() < self.BUFFER_TARGET:
                    self.buffer_underflows += 1
                    while self.queue.qsize() < (self.BUFFER_TARGET + 3) and self.running:
                        threading.Event().wait(0.002)
                try:
                    packet = self.queue.get(timeout=0.1)
                    audio_array = numpy.frombuffer(packet, dtype=numpy.float32).reshape(-1, self.CHANNELS)
                    if not audio_array.flags["C_CONTIGUOUS"]:
                        audio_array = numpy.ascontiguousarray(audio_array)

                    start = time.perf_counter()
                    output.play(audio_array)
                    self.elapsed = time.perf_counter() - start
                except queue.Empty:
                    self.buffer_underflows += 1
                    continue

    def _stats_thread(self):
        while self.running:
            time.sleep(0.5)
            #Calculate buffer latency:
            packet_duration = CURRENT_CONFIG.CLIENT_BLOCK_SIZE / CURRENT_CONFIG.CLIENT_SAMPLE_RATE
            current_queue_depth = self.queue.qsize()
            buffer_latency_ms = current_queue_depth * packet_duration * 1000

            #Calculate avarage jitter:
            avg_jitter_ms = (sum(self.jitters) / len(self.jitters) * 1000) if self.jitters else 0
            self.jitters.clear()

            self.stats_summary = f"""Latency: {buffer_latency_ms:.1f}ms | \
elapsed: {self.elapsed*1000:.3f} | \
queue treshold: {self.QUEUE_THRESHOLD} | \
Jitter: {avg_jitter_ms:.2f}ms | \
Queue Size: {current_queue_depth:<2} | \
Dropped Packets: {self.packets_dropped:<2} | \
Stutters (Underflows): {self.buffer_underflows:<4}"""
            CURRENT_MENU.refresh()
