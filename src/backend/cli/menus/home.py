from backend.cli.loops.base import Loop
from backend import CURRENT_MENU

class MainLoop(Loop):
    def __init__(self, server: Loop, client: Loop, config: Loop):
        super().__init__({
            1: server.run,
            2: client.run,
            3: config.run,
            4: CURRENT_MENU.break_current_menu
        })

    @staticmethod
    def message(*args):
        print("""# Options: Type ('number') to decide 
# 1. Server
# 2. Player
# 3. Configuration
# 4. Exit""")