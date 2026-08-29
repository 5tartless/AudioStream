from dataclasses import dataclass
from backend import RefreshVar

@dataclass
class AgentData:
    _type: any
    ip: str
    bridge: dict

    age: int = 0

class AgentManager():
    def __init__(self, on_agent_added: any, on_agent_removed: any):
        from backend.audio.audio_sender.udp import UDPSender

        self._agents: list[AgentData] = []
        self._ordered_agents = {
            UDPSender: RefreshVar(lambda: self.get_agents(_type=UDPSender))
        }
        self.on_agent_added = on_agent_added
        self.on_agent_removed = on_agent_removed

    def empty(self) -> bool:
        return not self._agents

    def pull_agents(self, _type: any) -> RefreshVar:
        return self._ordered_agents[_type]
    def set_agents(self, _type: any) -> None:
        self._ordered_agents[_type].set()

    def get_agents(self, _type: any = None) -> list[AgentData]:
        agents: list[dict] = []
        for agent in self._agents.copy():
            if (not _type) or (agent._type == _type):
                agents.append(agent)
        return agents

    def add_agent(self, _type, ip: str, bridge: dict) -> None:
        agent: AgentData = AgentData(_type=_type, ip=ip, bridge=bridge)
        self._agents.append(agent)
        self.set_agents(_type)
        self.on_agent_added(agent)

    def remove_agent(self, agent_data: AgentData) -> None:
        for agent in self._agents.copy():
            if agent == agent_data:
                self._agents.remove(agent)
                self.set_agents(agent._type)
                self.on_agent_removed(agent)
