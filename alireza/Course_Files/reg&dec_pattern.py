### Yek Mesal-e Kamel va Sade

# In piade-sazi az **3 bakhsh** tashkil shode:

#### 1. Sakhtane Class-e Registry (`registry.py`)
# In class yek dictionary az tamam-e factory-ha negah midare va yek decorator baraye sabt kardan expose mikone:

from collections.abc import Callable
from typing import Any

class AgentRegistry:
    def __init__(self) -> None:
        # Zakhire-sazie factory functions ba kelide name
        self._registry: dict[str, Callable[..., Any]] = {}

    def register(self, name: str):
        """Decorator baraye sabte agent factory."""
        def decorator(factory_fn: Callable[..., Any]):
            if name in self._registry:
                raise ValueError(f"Agent '{name}' az ghabl sabt shode!")
            self._registry[name] = factory_fn
            return factory_fn
        return decorator

    def get(self, name: str, **kwargs: Any) -> Any:
        """Sakht va daryafte agent dar zamane niaz (Lazy instantiation)."""
        if name not in self._registry:
            available = list(self._registry.keys())
            raise KeyError(f"Agent '{name}' peyda nashod! Mojoodi: {available}")

        factory = self._registry[name]
        return factory(**kwargs)

    def list_agents(self) -> list[str]:
        return list(self._registry.keys())

# Yek Singleton instance baraye kolle project
agent_registry = AgentRegistry()
#%%
#### 2. Sabt kardane Agent-ha ba Decorator (`agents.py`)
# Har agent tooye file-e khodesh bedune inke kari be baghie dashte bashe، khodesho register mikone:

# from registry import agent_registry

# Agent-e Avval: Web Researcher
@agent_registry.register("web_researcher")
def make_web_researcher(tier: str = "low"):
    print(f"Creating Web Researcher with model tier: {tier}")
    # Inja create_deep_agent ya LangGraph compile mishe
    return {"name": "web_researcher", "tools": ["web_search"], "tier": tier}


# Agent-e Dovvom: Code Interpreter
@agent_registry.register("code_interpreter")
def make_code_interpreter(sandbox_dir: str = "out/sandbox"):
    print(f"Creating Code Interpreter in: {sandbox_dir}")
    # Inja interpreter agent sakhte mishe
    return {"name": "code_interpreter", "tools": ["write_file", "execute"]}
#%%
#### 3. Estefade tooye Coordinator ya App (`app.py`)
# Hala Coordinator ya CLI aslan niazi nadare bedoone `make_web_researcher` ya `make_code_interpreter` koja va chejoori tarif shodan:

# from registry import agent_registry
import agents  # Faghat import mishe ta decorator-ha ejra beshan

def run_app():
    # 1. Didane hameye agent-haye mojood
    print("Available agents:", agent_registry.list_agents())
    # Khorooji: ['web_researcher', 'code_interpreter']

    # 2. Sakhtane agent ba esm (Dynamic Resolution)
    agent_name = "code_interpreter"
    selected_agent = agent_registry.get(agent_name, sandbox_dir="custom/sandbox")

    print("Loaded Agent:", selected_agent["name"])

if __name__ == "__main__":
    run_app()#### 3. Estefade tooye Coordinator ya App (`app.py`)
# Hala Coordinator ya CLI aslan niazi nadare bedoone `make_web_researcher` ya `make_code_interpreter` koja va chejoori tarif shodan: