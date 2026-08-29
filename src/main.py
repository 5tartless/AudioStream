from backend.cli.menus.home import MainLoop
from backend.cli.menus.server import ServerLoop
from backend.cli.menus.client import ClientLoop
from backend.cli.menus.config import ConfigLoop
from backend.agents import server, client

if __name__ == "__main__":
    server_agent = server.Server()
    client_agent = client.Client()

    server_loop = ServerLoop(server=server_agent)
    client_loop = ClientLoop(client=client_agent)
    config_loop = ConfigLoop()
    home_loop = MainLoop(
        server=server_loop,
        client=client_loop,
        config=config_loop
    )

    print("### AudioStream Console ###")
    home_loop.run()