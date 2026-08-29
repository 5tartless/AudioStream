from dataclasses import dataclass, asdict
import os, json, platform, socket

@dataclass
class Config():
    SERVER_SAMPLE_RATE: int = 44100
    SERVER_BLOCK_SIZE: int = 128
    SERVER_PORT: int = 5006
    SERVER_STREAM_PORT: int = 5005

    CLIENT_SAMPLE_RATE: int = 44100
    CLIENT_BLOCK_SIZE: int = 128
    CLIENT_PORT: int = 5006
    CLIENT_LISTEN_PORT: int = 5005

    USER_IP: str = None

class ConfigProvider():
    def __init__(self):
        from backend import APP_NAME
        self.DEFAULT_CONFIG = Config(USER_IP=self.get_ip_address())
        self.CONFIG_PATH = self.get_config_path()
        self.CONFIG_FILE_PATH = os.path.join(self.CONFIG_PATH, APP_NAME+".json")

    @staticmethod
    def get_config_path() -> str:
        system = platform.system()
        user_path = os.path.expanduser("~")
        config_path = {
            "Windows": "AppData\\Roaming",
            "Darwin": "Library/Application Support",
            "Linux": ".config"
        }.get(system, None)
        
        if config_path:
            path = os.path.join(user_path, config_path)
            if os.path.exists(path):
                return path
            else:
                print(f"[FATAL ERROR] Config path not found: {path}")
                exit()
        else:
            print("[FATAL ERROR] Unsopported Operating System: can't get config path.")
            exit()
    
    @staticmethod
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = None
        finally:
            s.close()
        return ip_address

    def read(self) -> Config:
        if os.path.exists(self.CONFIG_FILE_PATH):
            with open(self.CONFIG_FILE_PATH, "r") as file:
                data: dict = json.load(file)
                config: Config = Config(
                    SERVER_SAMPLE_RATE=data.get("SERVER_SAMPLE_RATE", 44100),
                    SERVER_BLOCK_SIZE=data.get("SERVER_BLOCK_SIZE", 128),
                    SERVER_PORT=data.get("SERVER_PORT", 5006),
                    SERVER_STREAM_PORT=data.get("SERVER_STREAM_PORT", 5005),

                    CLIENT_SAMPLE_RATE=data.get("CLIENT_SAMPLE_RATE", 44100),
                    CLIENT_BLOCK_SIZE=data.get("CLIENT_BLOCK_SIZE", 128),
                    CLIENT_PORT=data.get("CLIENT_PORT", 5006),
                    CLIENT_LISTEN_PORT=data.get("CLIENT_LISTEN_PORT", 5005),
                    
                    USER_IP=self.get_ip_address()
                )
                return config
        else:
            self.write(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

    def write(self, config: Config):
        with open(self.CONFIG_FILE_PATH, "w") as file:
            json.dump(asdict(config), file, indent=4)
