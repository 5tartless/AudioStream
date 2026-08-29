from backend.cli.loops.base import Loop
from backend.agents.base import Agent
from backend import AUDIO_DEVICE_PROVIDER, CURRENT_MENU

class DeviceLoop(Loop):
    def __init__(self, agent: Agent):
        def set_device(val):
            agent.io_device = val
            self.stop()

        #list all audio devices 
        self.devices = AUDIO_DEVICE_PROVIDER.devices()
        menu = {len(self.devices)+1: CURRENT_MENU.break_current_menu}
        for i, d in enumerate(self.devices):
            menu[i+1] = lambda device=d: set_device(device)
        super().__init__(menu)

    def message(self, *args):
        print("List of available Input and Output devices:")
        for i, device in enumerate(self.devices):
            print(f"# {i+1}. {device.name} ({device.type.capitalize()})")
        print(f"# {len(self.devices)+1}. Cancel")
        print("\n#! Select a device:")