from backend import CURRENT_MENU
from time import sleep as wait

class Loop():
    def __init__(self, menu: dict = {}):
        self.menu = menu
        self.running = False
        self.wait_time: float = 0.0
        self.unsaved_data: dict = {}

    @staticmethod
    def message(*args):
        pass

    def run(self):
        self.running = True

        self.message()
        while self.running:
            CURRENT_MENU.value = self
            try:
                if self.wait_time > 0.0:
                    wait(self.wait_time)
                    self.wait_time = 0.0
                    CURRENT_MENU.refresh()

                prompt = input("\n> ")
                if prompt == "/refresh":
                    CURRENT_MENU.refresh()
                    continue
                elif prompt == "/return":
                    exit()
                opt = int(prompt)
                self.menu[opt]()
            except Exception as e:
                self.wait_time = 1.25
                print(f"Wrong Input! \n{e.with_traceback()}")
            except KeyboardInterrupt:
                print("\n(!) Closing abruptly.")
                exit()
        self.unsaved_data.clear()

    def stop(self):
        self.running = False
