"""The Particle face of a Rung-2 domain capability: ``Specialist[TEngine, TInput, TReport]`` (ADR-0033).

This module re-exports from ``agentlab.workflows.base``.
"""

from agentlab.workflows.base import Specialist, WorkflowRunner

__all__ = ["Specialist", "WorkflowRunner"]
