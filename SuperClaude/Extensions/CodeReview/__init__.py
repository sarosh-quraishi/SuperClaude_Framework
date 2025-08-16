#!/usr/bin/env python3
"""
SuperClaude Multi-Agent Code Review System
Educational AI code review with specialized domain expertise

This extension provides comprehensive code review through 5 specialized agents:
- Clean Code Agent: Robert C. Martin's Clean Code principles
- Security Agent: OWASP Top 10 and security best practices  
- Performance Agent: Algorithm optimization and efficiency
- Design Patterns Agent: Gang of Four patterns and SOLID principles
- Testability Agent: TDD best practices and test design

Usage:
    /sc:code_review [file_path] - Comprehensive multi-agent review
    /sc:clean_code [file_path] - Clean Code analysis only
    /sc:security_review [file_path] - Security analysis only
    /sc:performance_review [file_path] - Performance analysis only
    /sc:design_patterns [file_path] - Design patterns analysis only
    /sc:testability [file_path] - Testability analysis only
"""

from .agents import (
    BaseAgent, CodeSuggestion, AgentResult, AgentCoordinator, SeverityLevel,
    CleanCodeAgent, SecurityAgent, PerformanceAgent, DesignPatternsAgent, TestabilityAgent,
    get_agent, get_all_agents, AVAILABLE_AGENTS
)

from .utils import (
    CodeParser, CodeContext, LanguageDetector, SupportedLanguage,
    OutputManager, InteractiveFormatter, ReportFormatter, JSONFormatter, ReviewSession
)

__version__ = "1.0.0"
__author__ = "SuperClaude Multi-Agent Code Review Team"

__all__ = [
    # Core classes
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
    
    # Agent utilities
    'get_agent',
    'get_all_agents',
    'AVAILABLE_AGENTS',
    
    # Code parsing
    'CodeParser',
    'CodeContext',
    'LanguageDetector', 
    'SupportedLanguage',
    
    # Output formatting
    'OutputManager',
    'InteractiveFormatter',
    'ReportFormatter',
    'JSONFormatter',
    'ReviewSession'
]

# Extension metadata for SuperClaude framework
EXTENSION_INFO = {
    'name': 'Multi-Agent Code Review',
    'version': __version__,
    'description': 'Educational AI code review with 5 specialized agents',
    'commands': [
        'sc:code_review',
        'sc:clean_code', 
        'sc:security_review',
        'sc:performance_review',
        'sc:design_patterns',
        'sc:testability'
    ],
    'agents': list(AVAILABLE_AGENTS.keys()),
    'supported_languages': [lang.value for lang in SupportedLanguage if lang != SupportedLanguage.UNKNOWN],
    'educational_focus': True,
    'requires_mcp': ['Context7', 'Sequential'],
    'optional_mcp': ['Magic', 'Playwright']
}