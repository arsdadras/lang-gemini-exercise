"""Middleware and hooks for agent pipelines.

This package is a placeholder for future middleware components such as
logging interceptors, rate limiters, authentication hooks, etc.
"""

from middleware.hitl import search_approval
from middleware.retry import retry_on_failure

__all__ = ["retry_on_failure", "search_approval"]
