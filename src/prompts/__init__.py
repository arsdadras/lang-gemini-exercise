"""System prompts for agents."""

<<<<<<< HEAD
from .research import build_research_prompt

__all__ = ["build_research_prompt"]
=======
from prompts.builder import build_system_prompt
from prompts.research import build_research_prompt

__all__ = ["build_research_prompt", "build_system_prompt"]
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
