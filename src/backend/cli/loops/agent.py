from backend import CURRENT_MENU
from backend.cli.loops import base, device
from backend.agents.base import Agent

class AgentLoop(base.Loop):
    def __init__(self, agent: Agent, menu = {}):
        super().__init__(menu)
        self.agent: Agent = agent

    def toggle_status(self, conditioner: any, callback: any):
        if conditioner():
            callback()
        CURRENT_MENU().wait_time = 1

    def set_io_device(self):
        device.DeviceLoop(agent=self.agent).run()

    def set_port(self, callback: any, *args):
        prompt = input("Port> ")
        if prompt.strip().isdigit():
            callback(int(prompt), *args)
            CURRENT_MENU.refresh()
        else:
            print("(!) Please enter a port number.")
            CURRENT_MENU.value.wait_time = 1
