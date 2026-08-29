from backend import RefreshVar
import threading

class ConnectionWatcher():
    def __init__(self, agents: RefreshVar, on_disconnect: any):
        self.agents: RefreshVar = agents
        self.on_disconnect: any = on_disconnect
        self.running: bool = False
        self.reset()
    
    #-force stop
    def kill_all(self, custom_callback: any = None) -> None:
        for agent in self.agents():
            custom_callback(agent) if custom_callback else self.on_disconnect(agent)
    def start(self) -> None:
        self.running = True
        self.watcher_thread.start()
    def stop(self) -> None:
        self.running = False
        self.watcher_thread: threading.Thread
        if self.watcher_thread.is_alive():
            self.watcher_thread.join()
        self.reset()

    def reset(self):
        self.watcher_thread = threading.Thread(target=self._watch, daemon=True)

    def _watch(self) -> None:
        pass
