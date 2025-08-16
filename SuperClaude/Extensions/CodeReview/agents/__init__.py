#!/usr/bin/env python3
"""
SuperClaude Multi-Agent Code Review System
Educational AI code review with specialized domain expertise
"""

from .base_agent import BaseAgent, CodeSuggestion, AgentResult, AgentCoordinator, SeverityLevel
from .clean_code_agent import CleanCodeAgent, CleanCodePrinciples
from .security_agent import SecurityAgent, SecurityPrinciples
from .performance_agent import PerformanceAgent, PerformancePrinciples
from .design_patterns_agent import DesignPatternsAgent, DesignPatternsPrinciples
from .testability_agent import TestabilityAgent, TestabilityPrinciples

__all__ = [
    # Base classes
    'BaseAgent',
    'CodeSuggestion', 
    'AgentResult',
    'AgentCoordinator',
    'SeverityLevel',
    
    # Specialized agents
    'CleanCodeAgent',
    'SecurityAgent',
    'PerformanceAgent',
    'DesignPatternsAgent',
    'TestabilityAgent',
    
    # Reference classes
    'CleanCodePrinciples',
    'SecurityPrinciples',
    'PerformancePrinciples',
    'DesignPatternsPrinciples',
    'TestabilityPrinciples'
]

# Agent registry for easy access
AVAILABLE_AGENTS = {
    'clean_code': CleanCodeAgent,
    'security': SecurityAgent,
    'performance': PerformanceAgent,
    'design_patterns': DesignPatternsAgent,
    'testability': TestabilityAgent
}

def get_agent(agent_name: str) -> BaseAgent:
    """Factory function to create agent instances"""
    agent_class = AVAILABLE_AGENTS.get(agent_name.lower())
    if not agent_class:
        available = ', '.join(AVAILABLE_AGENTS.keys())
        raise ValueError(f"Unknown agent: {agent_name}. Available agents: {available}")
    return agent_class()

def get_all_agents() -> list[BaseAgent]:
    """Get instances of all available agents"""
    return [agent_class() for agent_class in AVAILABLE_AGENTS.values()]