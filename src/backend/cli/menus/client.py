from backend.cli.loops.agent import AgentLoop
from backend.agents.client import Client
from backend import CURRENT_MENU, CURRENT_CONFIG

class ClientLoop(AgentLoop):
    def __init__(self, client: Client):
        super().__init__(
            agent=client, 
            menu={
                1: self.toggle_status,
                2: self.set_io_device,
                3: self.set_srv_ip,
                4: lambda: self.set_port(srv=True),
                5: lambda: self.set_port(srv=False),
                6: CURRENT_MENU.break_current_menu,
            }
        )
    
    def message(self, *args):
        print(f"""#Player: 
Active: {self.agent.active}
Server IP: {self.agent.server_ip or 'Not set'}:{CURRENT_CONFIG.CLIENT_PORT}
Output device: {self.agent.io_device.name+f' ({self.agent.io_device.type.capitalize()})' if self.agent.io_device else 'Not set'}
Listening Port: {CURRENT_CONFIG.CLIENT_LISTEN_PORT or 'Not set'}
{f'\nStats: {self.agent.audio_manager.stats_summary}\n' if self.agent.active else ''}
-----------------------------------

# 1. {'Disconnect from current' if self.agent.active else 'Connect to'} server

# 2. Set output device
# 3. Set server ip
# 4. Set server port
# 5. Set listening port
# 6. Exit""")
    
    def set_srv_ip(self):
        from socket import inet_aton, error
        
        prompt = input("IP> ")
        try:
            inet_aton(prompt)
            self.agent.server_ip = prompt
            CURRENT_MENU.refresh()
        except error:
            print("(!) Please enter IPv4")
            CURRENT_MENU.value.wait_time = 1
    
    def set_port(self, srv: bool):
        def callback(prompt, srv):
            if srv:
                CURRENT_CONFIG.CLIENT_PORT = prompt
            else:
                CURRENT_CONFIG.CLIENT_LISTEN_PORT = prompt
        return super().set_port(callback, srv)

    def toggle_status(self):
        def conditioner() -> bool:
            if not self.agent.active:
                if not all((self.agent.server_ip, self.agent.io_device, CURRENT_CONFIG.CLIENT_PORT, CURRENT_CONFIG.CLIENT_LISTEN_PORT)):
                    print("(!) Fill all options below before connecting.")
                    return False
                else:
                    print(f"# Connecting to {self.agent.server_ip}:{CURRENT_CONFIG.CLIENT_PORT}...")
                    return True
            else:
                return True
        return super().toggle_status(conditioner, self.agent.toggle_status)
