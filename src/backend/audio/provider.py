from dataclasses import dataclass
import soundcard as sc

@dataclass
class AudioDevice():
    id: str
    name: str
    type: str
    default: bool

class AudioDeviceProvider():
    def list_output_devices(self):
        output_devices: list = []
        for speaker in sc.all_speakers():
            output_devices.append(
                AudioDevice(
                    id=speaker.id,
                    name=speaker.name,
                    type="output",
                    default=speaker.name == sc.default_speaker().name
                )
            )

        return output_devices

    def list_input_devices(self):
        input_devices: list = []
        for microphone in sc.all_microphones():
            input_devices.append(
                AudioDevice(
                    id=microphone.id,
                    name=microphone.name,
                    type="input",
                    default=microphone.name == sc.default_microphone().name
                )
            )
        return input_devices

    def devices(self) -> list:
        return [
            *self.list_input_devices(), *self.list_output_devices()
        ]
    
    def devices_by_type(self):
        return {
            "input": [*self.list_input_devices()],
            "output": [*self.list_output_devices()]
        }
    
    def device_type(self, device) -> str | None:
        if device in self.list_input_devices():
            return "input"
        elif device in self.list_output_devices():
            return "output"
        else: 
            return None
