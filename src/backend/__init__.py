from os import system, name
from .audio.provider import AudioDeviceProvider
from .config.provider import ConfigProvider

class RefreshVar():
    def __init__(self, setter: any, *args):
        self.setter = lambda: setter(*args)
        self._value: any = self.setter()
        self.on_set: any = None

    def set(self):
        self._value = self.setter()
        if self.on_set: self.on_set()

    def __call__(self, *args, **kwds):
        return self._value

class CallbackVar():
    def __init__(self, value: any, callback):
        self._value: any = value
        self.callback = callback

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_val):
        if self._value != new_val:
            self._value = new_val
            self.callback(new_val)
    
    def __call__(self, *args, **kwds) -> any:
        return self.value
class CurrentMenu(CallbackVar):
    def __init__(self, value: any = None):
        super().__init__(value, self.refresh)

    def refresh(self, *args):
        system('cls' if name == 'nt' else 'clear')
        self.value.message()

    def break_current_menu(self):
        self.value.stop()

APP_NAME = "AudioStream"
CONFIG_PROVIDER = ConfigProvider()
CURRENT_CONFIG = CONFIG_PROVIDER.read()
CURRENT_MENU = CurrentMenu()
AUDIO_DEVICE_PROVIDER = AudioDeviceProvider()