from backend.cli.loops.base import Loop
from backend import CURRENT_MENU

class ConfigLoop(Loop):
    def __init__(self):
        super().__init__({
            1: CURRENT_MENU.break_current_menu
        })

    @staticmethod
    def message(*args):
        print("# 1. Exit")