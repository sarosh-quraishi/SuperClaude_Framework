#!/usr/bin/env python3
"""
Utilities for SuperClaude Multi-Agent Code Review System
"""

from .code_parser import CodeParser, CodeContext, LanguageDetector, SupportedLanguage
from .output_formatter import OutputManager, InteractiveFormatter, ReportFormatter, JSONFormatter, ReviewSession
from .interactive_diff_reviewer import InteractiveDiffReviewer, ReviewAction, ReviewDecision, DiffHunk

# Import new critical enhancements
try:
    from .claude_api_integration import ClaudeAPIIntegration, APIConfig, APIMetrics, create_api_config_from_env
    CLAUDE_API_AVAILABLE = True
except ImportError:
    CLAUDE_API_AVAILABLE = False

try:
    from .collaboration_engine import (
        CrossAgentCollaborationEngine, ProjectContext, Conflict, Synergy, 
        CollaborationReport, ConflictType, ResolutionStrategy, StrategyEffectiveness
    )
    COLLABORATION_ENGINE_AVAILABLE = True
except ImportError:
    COLLABORATION_ENGINE_AVAILABLE = False

try:
    from .continuous_learning import (
        ContinuousLearningEngine, SuggestionFeedback, AgentPerformanceMetrics, 
        PrincipleEffectiveness, create_learning_engine
    )
    CONTINUOUS_LEARNING_AVAILABLE = True
except ImportError:
    CONTINUOUS_LEARNING_AVAILABLE = False

__all__ = [
    'CodeParser',
    'CodeContext', 
    'LanguageDetector',
    'SupportedLanguage',
    'OutputManager',
    'InteractiveFormatter',
    'ReportFormatter', 
    'JSONFormatter',
    'ReviewSession',
    'InteractiveDiffReviewer',
    'ReviewAction',
    'ReviewDecision', 
    'DiffHunk'
]

# Add new modules to exports if available
if CLAUDE_API_AVAILABLE:
    __all__.extend([
        'ClaudeAPIIntegration',
        'APIConfig', 
        'APIMetrics',
        'create_api_config_from_env'
    ])

if COLLABORATION_ENGINE_AVAILABLE:
    __all__.extend([
        'CrossAgentCollaborationEngine',
        'ProjectContext',
        'Conflict',
        'Synergy',
        'CollaborationReport',
        'ConflictType',
        'ResolutionStrategy',
        'StrategyEffectiveness'
    ])

if CONTINUOUS_LEARNING_AVAILABLE:
    __all__.extend([
        'ContinuousLearningEngine',
        'SuggestionFeedback',
        'AgentPerformanceMetrics',
        'PrincipleEffectiveness',
        'create_learning_engine'
    ])