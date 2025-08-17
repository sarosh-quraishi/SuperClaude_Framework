#!/usr/bin/env python3
"""
Configuration management for SuperClaude Multi-Agent Code Review System
Centralized configuration with environment variable support and validation
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ClaudeAPIConfig:
    """Configuration for Claude API integration"""
    api_key: str = ""
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 50
    base_url: str = "https://api.anthropic.com"
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv('ANTHROPIC_API_KEY', '')


@dataclass
class ProjectConfig:
    """Project-specific configuration for code review"""
    priority: str = "balanced"  # performance, security, maintainability, balanced
    development_phase: str = "development"  # prototype, development, production
    team_size: int = 5
    performance_critical: bool = False
    security_sensitive: bool = False
    legacy_system: bool = False
    test_coverage: float = 0.7
    technical_debt_level: str = "medium"  # low, medium, high
    
    def __post_init__(self):
        # Validate priority
        valid_priorities = ["performance", "security", "maintainability", "balanced"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        
        # Validate development phase
        valid_phases = ["prototype", "development", "production"]
        if self.development_phase not in valid_phases:
            raise ValueError(f"Development phase must be one of: {valid_phases}")
        
        # Validate technical debt level
        valid_debt_levels = ["low", "medium", "high"]
        if self.technical_debt_level not in valid_debt_levels:
            raise ValueError(f"Technical debt level must be one of: {valid_debt_levels}")
        
        # Validate ranges
        if not 0.0 <= self.test_coverage <= 1.0:
            raise ValueError("Test coverage must be between 0.0 and 1.0")
        
        if self.team_size < 1:
            raise ValueError("Team size must be at least 1")


@dataclass
class InteractiveConfig:
    """Configuration for interactive review interface"""
    use_colors: bool = True
    context_lines: int = 3
    auto_clear_screen: bool = True
    enable_batch_mode: bool = True
    default_editor: str = "nano"
    max_suggestions_per_screen: int = 1
    
    def __post_init__(self):
        # Override with environment variables
        self.use_colors = os.getenv('CODE_REVIEW_NO_COLOR', 'false').lower() != 'true'
        self.context_lines = int(os.getenv('CODE_REVIEW_CONTEXT_LINES', str(self.context_lines)))
        self.default_editor = os.getenv('EDITOR', self.default_editor)


@dataclass
class LanguageConfig:
    """Language-specific configuration"""
    style_guide: str
    complexity_threshold: int
    line_length: int
    naming_convention: str
    security_patterns: List[str] = field(default_factory=list)
    performance_patterns: List[str] = field(default_factory=list)
    common_anti_patterns: List[str] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    enabled_agents: List[str] = field(default_factory=lambda: [
        "Clean Code Agent",
        "Security Agent", 
        "Performance Agent",
        "Design Patterns Agent",
        "Testability Agent"
    ])
    agent_weights: Dict[str, float] = field(default_factory=lambda: {
        "Security Agent": 1.0,
        "Performance Agent": 0.8,
        "Clean Code Agent": 0.6,
        "Design Patterns Agent": 0.5,
        "Testability Agent": 0.4
    })
    min_confidence_threshold: float = 0.5
    min_impact_threshold: float = 3.0
    enable_fallback_analysis: bool = True
    
    # Multi-language support
    language_configs: Dict[str, LanguageConfig] = field(default_factory=lambda: {
        "python": LanguageConfig(
            style_guide="PEP 8",
            complexity_threshold=10,
            line_length=88,
            naming_convention="snake_case",
            security_patterns=["sql_injection", "command_injection", "path_traversal", "xss"],
            performance_patterns=["list_comprehension", "generator", "caching", "lazy_loading"],
            common_anti_patterns=["god_class", "long_method", "duplicate_code", "magic_numbers"]
        ),
        "javascript": LanguageConfig(
            style_guide="Airbnb",
            complexity_threshold=15,
            line_length=100,
            naming_convention="camelCase",
            security_patterns=["xss", "prototype_pollution", "eval_injection", "regex_dos"],
            performance_patterns=["debouncing", "memoization", "lazy_loading", "tree_shaking"],
            common_anti_patterns=["callback_hell", "global_variables", "implicit_globals", "blocking_operations"]
        ),
        "typescript": LanguageConfig(
            style_guide="Microsoft TypeScript",
            complexity_threshold=12,
            line_length=120,
            naming_convention="camelCase",
            security_patterns=["type_confusion", "any_abuse", "unsafe_casting", "xss"],
            performance_patterns=["type_guards", "const_assertions", "tree_shaking", "lazy_loading"],
            common_anti_patterns=["any_type_overuse", "non_null_assertion", "type_assertion_abuse"]
        ),
        "java": LanguageConfig(
            style_guide="Google Java Style",
            complexity_threshold=12,
            line_length=120,
            naming_convention="camelCase",
            security_patterns=["deserialization", "injection", "xxe", "path_traversal"],
            performance_patterns=["streams", "collections", "caching", "lazy_initialization"],
            common_anti_patterns=["god_class", "singleton_abuse", "primitive_obsession", "anemic_model"]
        ),
        "go": LanguageConfig(
            style_guide="Effective Go",
            complexity_threshold=10,
            line_length=100,
            naming_convention="mixedCaps",
            security_patterns=["sql_injection", "command_injection", "path_traversal", "race_conditions"],
            performance_patterns=["goroutines", "channels", "sync_pool", "buffer_reuse"],
            common_anti_patterns=["goroutine_leaks", "channel_blocking", "interface_pollution"]
        ),
        "rust": LanguageConfig(
            style_guide="Rust Style Guide",
            complexity_threshold=8,
            line_length=100,
            naming_convention="snake_case",
            security_patterns=["unsafe_usage", "memory_safety", "integer_overflow", "race_conditions"],
            performance_patterns=["zero_copy", "iterator_chains", "cow", "arena_allocation"],
            common_anti_patterns=["clone_abuse", "unwrap_abuse", "string_allocation", "box_everything"]
        ),
        "csharp": LanguageConfig(
            style_guide="Microsoft C# Conventions",
            complexity_threshold=12,
            line_length=120,
            naming_convention="PascalCase",
            security_patterns=["deserialization", "sql_injection", "ldap_injection", "xml_injection"],
            performance_patterns=["linq", "async_await", "value_types", "object_pooling"],
            common_anti_patterns=["exception_handling_abuse", "async_void", "dispose_pattern_violation"]
        ),
        "cpp": LanguageConfig(
            style_guide="Google C++ Style",
            complexity_threshold=15,
            line_length=80,
            naming_convention="snake_case",
            security_patterns=["buffer_overflow", "use_after_free", "double_free", "integer_overflow"],
            performance_patterns=["move_semantics", "raii", "zero_cost_abstractions", "template_metaprogramming"],
            common_anti_patterns=["manual_memory_management", "raw_pointers", "global_state", "deep_inheritance"]
        )
    })
    
    def get_language_config(self, language: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language"""
        return self.language_configs.get(language.lower())
    
    def add_language_config(self, language: str, config: LanguageConfig):
        """Add or update language configuration"""
        self.language_configs[language.lower()] = config


@dataclass
class CodeReviewConfig:
    """Main configuration container"""
    claude_api: ClaudeAPIConfig = field(default_factory=ClaudeAPIConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)
    interactive: InteractiveConfig = field(default_factory=InteractiveConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    
    # Global settings
    enable_collaboration_engine: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    output_format: str = "interactive"  # interactive, report, json
    
    # Cost management
    enable_cost_tracking: bool = True
    monthly_budget_limit: float = 100.0  # USD
    cost_alert_threshold: float = 0.8  # Alert at 80% of budget
    
    def __post_init__(self):
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {valid_log_levels}")
        
        # Validate output format
        valid_formats = ["interactive", "report", "json"]
        if self.output_format not in valid_formats:
            raise ValueError(f"Output format must be one of: {valid_formats}")


class ConfigManager:
    """Manages configuration loading, validation, and saving"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.logger = logging.getLogger(__name__)
        self._config: Optional[CodeReviewConfig] = None
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Try user config directory first
        user_config_dir = os.path.expanduser("~/.superclaude")
        if not os.path.exists(user_config_dir):
            try:
                os.makedirs(user_config_dir, exist_ok=True)
            except PermissionError:
                pass
        
        return os.path.join(user_config_dir, "code_review_config.json")
    
    def load_config(self) -> CodeReviewConfig:
        """Load configuration from file or create default"""
        if self._config:
            return self._config
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Convert nested dictionaries to dataclass instances
                self._config = self._dict_to_config(config_data)
                self.logger.info(f"Loaded configuration from {self.config_path}")
            else:
                # Create default configuration
                self._config = CodeReviewConfig()
                self.save_config(self._config)
                self.logger.info(f"Created default configuration at {self.config_path}")
                
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}, using defaults")
            self._config = CodeReviewConfig()
        
        return self._config
    
    def save_config(self, config: CodeReviewConfig) -> bool:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Convert to dictionary and save
            config_dict = asdict(config)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> CodeReviewConfig:
        """Convert dictionary to CodeReviewConfig"""
        
        # Handle nested configurations
        claude_api_data = config_data.get('claude_api', {})
        project_data = config_data.get('project', {})
        interactive_data = config_data.get('interactive', {})
        agents_data = config_data.get('agents', {})
        
        return CodeReviewConfig(
            claude_api=ClaudeAPIConfig(**claude_api_data),
            project=ProjectConfig(**project_data),
            interactive=InteractiveConfig(**interactive_data),
            agents=AgentConfig(**agents_data),
            enable_collaboration_engine=config_data.get('enable_collaboration_engine', True),
            enable_logging=config_data.get('enable_logging', True),
            log_level=config_data.get('log_level', 'INFO'),
            output_format=config_data.get('output_format', 'interactive')
        )
    
    def update_config(self, **kwargs) -> CodeReviewConfig:
        """Update configuration with new values"""
        config = self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.save_config(config)
        return config
    
    def validate_config(self, config: CodeReviewConfig) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate API key
        if not config.claude_api.api_key:
            issues.append("Claude API key is required (set ANTHROPIC_API_KEY environment variable)")
        
        # Validate API configuration
        if config.claude_api.max_tokens < 1000:
            issues.append("Max tokens should be at least 1000 for meaningful analysis")
        
        if not 0.0 <= config.claude_api.temperature <= 1.0:
            issues.append("Temperature must be between 0.0 and 1.0")
        
        # Validate agent configuration
        if not config.agents.enabled_agents:
            issues.append("At least one agent must be enabled")
        
        if config.agents.min_confidence_threshold < 0.0 or config.agents.min_confidence_threshold > 1.0:
            issues.append("Confidence threshold must be between 0.0 and 1.0")
        
        if config.agents.min_impact_threshold < 1.0 or config.agents.min_impact_threshold > 10.0:
            issues.append("Impact threshold must be between 1.0 and 10.0")
        
        return issues
    
    def estimate_monthly_cost(self, config: CodeReviewConfig) -> Dict[str, Any]:
        """Estimate monthly costs based on configuration and usage patterns"""
        # Claude API pricing (approximate as of 2024)
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},  # per 1K tokens
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075}
        }
        
        model_pricing = pricing.get(config.claude_api.model, pricing["claude-3-5-sonnet-20241022"])
        
        # Estimate usage patterns
        avg_input_tokens = 2000  # Typical code analysis prompt
        avg_output_tokens = config.claude_api.max_tokens * 0.7
        
        # Calculate requests based on team and project characteristics
        base_requests_per_person_per_day = 10
        
        # Adjust based on project characteristics
        multiplier = 1.0
        if config.project.development_phase == "production":
            multiplier *= 1.5  # More thorough reviews
        if config.project.security_sensitive:
            multiplier *= 1.3  # More security analysis
        if config.project.performance_critical:
            multiplier *= 1.2  # More performance analysis
        if config.project.technical_debt_level == "high":
            multiplier *= 1.4  # More cleanup needed
        
        requests_per_day = config.project.team_size * base_requests_per_person_per_day * multiplier
        requests_per_month = requests_per_day * 22  # 22 working days
        
        # Calculate costs
        input_cost_per_month = (requests_per_month * avg_input_tokens / 1000) * model_pricing["input"]
        output_cost_per_month = (requests_per_month * avg_output_tokens / 1000) * model_pricing["output"]
        total_cost_per_month = input_cost_per_month + output_cost_per_month
        
        # Budget analysis
        budget_utilization = (total_cost_per_month / config.monthly_budget_limit) if config.monthly_budget_limit > 0 else 0
        
        return {
            "estimated_monthly_cost": round(total_cost_per_month, 2),
            "input_cost": round(input_cost_per_month, 2),
            "output_cost": round(output_cost_per_month, 2),
            "requests_per_month": int(requests_per_month),
            "requests_per_day": round(requests_per_day, 1),
            "total_tokens_per_month": int(requests_per_month * (avg_input_tokens + avg_output_tokens)),
            "cost_per_request": round(total_cost_per_month / requests_per_month, 4),
            "budget_limit": config.monthly_budget_limit,
            "budget_utilization": round(budget_utilization, 2),
            "budget_status": "over_budget" if budget_utilization > 1.0 else 
                           "warning" if budget_utilization > config.cost_alert_threshold else "ok",
            "model": config.claude_api.model,
            "team_size": config.project.team_size,
            "usage_multiplier": round(multiplier, 2)
        }


def setup_logging(config: CodeReviewConfig) -> None:
    """Setup logging based on configuration"""
    if not config.enable_logging:
        logging.disable(logging.CRITICAL)
        return
    
    log_level = getattr(logging, config.log_level.upper())
    
    # Create logs directory
    log_dir = os.path.expanduser("~/.superclaude/logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'code_review.log')),
            logging.StreamHandler()
        ]
    )


def create_config_from_env() -> CodeReviewConfig:
    """Create configuration from environment variables"""
    
    config = CodeReviewConfig()
    
    # Claude API configuration from environment
    config.claude_api.api_key = os.getenv('ANTHROPIC_API_KEY', '')
    config.claude_api.model = os.getenv('CLAUDE_MODEL', config.claude_api.model)
    config.claude_api.max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', str(config.claude_api.max_tokens)))
    config.claude_api.temperature = float(os.getenv('CLAUDE_TEMPERATURE', str(config.claude_api.temperature)))
    config.claude_api.timeout = int(os.getenv('CLAUDE_TIMEOUT', str(config.claude_api.timeout)))
    config.claude_api.rate_limit_rpm = int(os.getenv('CLAUDE_RATE_LIMIT_RPM', str(config.claude_api.rate_limit_rpm)))
    
    # Project configuration from environment
    config.project.priority = os.getenv('PROJECT_PRIORITY', config.project.priority)
    config.project.development_phase = os.getenv('DEVELOPMENT_PHASE', config.project.development_phase)
    config.project.performance_critical = os.getenv('PERFORMANCE_CRITICAL', 'false').lower() == 'true'
    config.project.security_sensitive = os.getenv('SECURITY_SENSITIVE', 'false').lower() == 'true'
    config.project.legacy_system = os.getenv('LEGACY_SYSTEM', 'false').lower() == 'true'
    
    # Interactive configuration from environment
    config.interactive.use_colors = os.getenv('CODE_REVIEW_NO_COLOR', 'false').lower() != 'true'
    config.interactive.context_lines = int(os.getenv('CODE_REVIEW_CONTEXT_LINES', str(config.interactive.context_lines)))
    
    # Global settings from environment
    config.enable_collaboration_engine = os.getenv('ENABLE_COLLABORATION_ENGINE', 'true').lower() == 'true'
    config.log_level = os.getenv('LOG_LEVEL', config.log_level)
    config.output_format = os.getenv('OUTPUT_FORMAT', config.output_format)
    
    return config


def get_default_config() -> CodeReviewConfig:
    """Get default configuration instance"""
    return CodeReviewConfig()


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    
    return _config_manager


def get_config() -> CodeReviewConfig:
    """Get current configuration"""
    return get_config_manager().load_config()


if __name__ == "__main__":
    # Configuration testing and setup
    print("SuperClaude Code Review Configuration Manager")
    print("=" * 50)
    
    # Load or create configuration
    manager = get_config_manager()
    config = manager.load_config()
    
    # Validate configuration
    issues = manager.validate_config(config)
    
    if issues:
        print("Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid")
    
    print(f"\nConfiguration file: {manager.config_path}")
    print(f"Claude API configured: {'✅' if config.claude_api.api_key else '❌'}")
    print(f"Enabled agents: {len(config.agents.enabled_agents)}")
    print(f"Collaboration engine: {'✅' if config.enable_collaboration_engine else '❌'}")
    print(f"Output format: {config.output_format}")