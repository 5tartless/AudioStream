from backend.cli.loops.agent import AgentLoop
from backend import CURRENT_MENU, CURRENT_CONFIG

class ServerLoop(AgentLoop):
    def __init__(self, server):
        super().__init__(
            agent=server,
            menu={
                1: self.toggle_status,
                2: self.conf_srv_name,
                3: self.set_io_device,
                4: lambda: self.set_port(srv=True),
                5: lambda: self.set_port(srv=False),
                6: CURRENT_MENU.break_current_menu
            }
        )
    
    def message(self, *args):
        print(f"""#Server: 
Your current IP is: {CURRENT_CONFIG.USER_IP}
Server port: {CURRENT_CONFIG.SERVER_PORT}
Server name: {self.agent.name or 'Not set'}

Streaming device: {'Not set' if not self.agent.io_device else self.agent.io_device.name+f' ({self.agent.io_device.type.capitalize()})'}
Streaming port: {CURRENT_CONFIG.SERVER_STREAM_PORT}
Online: {self.agent.active}
{f'\nActive clients: {' | '.join([c.ip for c in self.agent.agent_manager.get_agents()])}\n' if self.agent.active and not self.agent.agent_manager.empty() else ''}
------------------------------------

# 1. {'Start' if not self.agent.active else 'Stop'}
# 2. Configure server name
# 3. Set streaming device
# 4. Set server port
# 5. Set streaming port 
# 6. Exit""")
    
    def toggle_status(self):
        def conditioner() -> bool:
            if not self.agent.active:
                if not all((self.agent.name, self.agent.io_device, CURRENT_CONFIG.SERVER_PORT, CURRENT_CONFIG.SERVER_STREAM_PORT)):
                    print("(!) Make sure every field is set.")
                    return False
                else:
                    return True
            else:
                return True
        return super().toggle_status(conditioner, self.agent.toggle_status)

    def set_port(self, srv: bool):
        def callback(prompt, srv):
            if srv:
                CURRENT_CONFIG.SERVER_PORT = prompt
            else:
                CURRENT_CONFIG.SERVER_STREAM_PORT = prompt
        return super().set_port(callback, srv)

    def conf_srv_name(self):
        prompt = ""
        print("#Type your new server name:")
        while not prompt.strip():
            prompt = input("> ")
            if not prompt.strip():
                CURRENT_MENU.refresh()
                print("\n#! Please enter something.")
        self.agent.name = prompt
        CURRENT_MENU.refresh()
