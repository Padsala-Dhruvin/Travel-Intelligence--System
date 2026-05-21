"""
Entry point. ADK auto-discovers agents named `root_agent` when you run `adk web`.
"""
from agents.coordinator import root_agent

# ADK convention: expose root_agent at the module level
__all__ = ["root_agent"]