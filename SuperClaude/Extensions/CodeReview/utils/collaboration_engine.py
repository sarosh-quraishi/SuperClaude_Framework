#!/usr/bin/env python3
"""
Cross-Agent Collaboration Engine for SuperClaude Multi-Agent Code Review System
Intelligent coordination and conflict resolution between specialized agents
"""

import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import re

from ..agents import CodeSuggestion, AgentResult, SeverityLevel


class ConflictType(Enum):
    """Types of conflicts between agent suggestions"""
    PHILOSOPHICAL = "philosophical"  # Different approaches to same problem
    OVERLAPPING = "overlapping"      # Multiple agents targeting same issue
    CONTRADICTORY = "contradictory"  # Mutually exclusive suggestions
    PRIORITY = "priority"            # Different priority assessments


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts"""
    CONTEXT_DRIVEN = "context_driven"      # Resolve based on project context
    IMPACT_WEIGHTED = "impact_weighted"    # Higher impact suggestion wins
    AGENT_HIERARCHY = "agent_hierarchy"    # Security > Performance > Clean Code
    USER_CHOICE = "user_choice"            # Let user decide
    SYNTHESIS = "synthesis"                # Combine suggestions


@dataclass
class ProjectContext:
    """Context about the project to guide decision making"""
    priority: str = "balanced"  # performance, security, maintainability, balanced
    development_phase: str = "development"  # prototype, development, production
    team_size: int = 5
    performance_critical: bool = False
    security_sensitive: bool = False
    legacy_system: bool = False
    test_coverage: float = 0.7
    technical_debt_level: str = "medium"  # low, medium, high


@dataclass
class Conflict:
    """Represents a conflict between agent suggestions"""
    conflict_id: str
    conflict_type: ConflictType
    involved_agents: List[str]
    conflicting_suggestions: List[CodeSuggestion]
    line_number: Optional[int]
    description: str
    impact_assessment: float
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolved_suggestion: Optional[CodeSuggestion] = None
    resolution_rationale: Optional[str] = None


@dataclass
class Synergy:
    """Represents synergistic suggestions that work better together"""
    synergy_id: str
    involved_agents: List[str]
    synergistic_suggestions: List[CodeSuggestion]
    combined_impact: float
    synthesis_description: str
    implementation_order: List[str]


@dataclass
class CollaborationReport:
    """Report of agent collaboration analysis"""
    total_suggestions: int
    conflicts: List[Conflict]
    synergies: List[Synergy]
    priority_matrix: Dict[str, float]
    recommended_focus_areas: List[str]
    overall_collaboration_score: float


class CrossAgentCollaborationEngine:
    """Intelligent coordination between specialized agents"""
    
    def __init__(self, project_context: Optional[ProjectContext] = None):
        self.project_context = project_context or ProjectContext()
        self.logger = logging.getLogger(__name__)
        
        # Agent hierarchy for conflict resolution (higher value = higher priority)
        self.agent_hierarchy = {
            "Security Agent": 100,
            "Performance Agent": 80,
            "Clean Code Agent": 60,
            "Design Patterns Agent": 50,
            "Testability Agent": 40
        }
    
    def analyze_collaboration(self, agent_results: List[AgentResult]) -> CollaborationReport:
        """Analyze how agent suggestions interact and collaborate"""
        
        all_suggestions = []
        for result in agent_results:
            all_suggestions.extend(result.suggestions)
        
        # Find conflicts and synergies
        conflicts = self._detect_conflicts(agent_results)
        synergies = self._find_synergies(agent_results)
        
        # Establish priority matrix
        priority_matrix = self._establish_priority_matrix(agent_results)
        
        # Recommend focus areas
        focus_areas = self._recommend_focus_areas(agent_results, conflicts, synergies)
        
        # Calculate collaboration score
        collaboration_score = self._calculate_collaboration_score(conflicts, synergies, len(all_suggestions))
        
        return CollaborationReport(
            total_suggestions=len(all_suggestions),
            conflicts=conflicts,
            synergies=synergies,
            priority_matrix=priority_matrix,
            recommended_focus_areas=focus_areas,
            overall_collaboration_score=collaboration_score
        )
    
    def resolve_conflicts(self, conflicts: List[Conflict]) -> List[Conflict]:
        """Resolve conflicts using intelligent strategies"""
        
        resolved_conflicts = []
        
        for conflict in conflicts:
            resolved_conflict = self._resolve_single_conflict(conflict)
            resolved_conflicts.append(resolved_conflict)
        
        return resolved_conflicts
    
    def _detect_conflicts(self, agent_results: List[AgentResult]) -> List[Conflict]:
        """Detect various types of conflicts between agent suggestions"""
        
        conflicts = []
        all_suggestions = []
        
        # Collect all suggestions with agent info
        for result in agent_results:
            for suggestion in result.suggestions:
                all_suggestions.append((suggestion, result.agent_name))
        
        # Group suggestions by line number for overlap detection
        suggestions_by_line = defaultdict(list)
        for suggestion, agent_name in all_suggestions:
            if suggestion.line_number:
                suggestions_by_line[suggestion.line_number].append((suggestion, agent_name))
        
        # Check for line-level conflicts
        for line_num, line_suggestions in suggestions_by_line.items():
            if len(line_suggestions) > 1:
                conflict = self._analyze_line_conflict(line_num, line_suggestions)
                if conflict:
                    conflicts.append(conflict)
        
        # Check for philosophical conflicts
        philosophical_conflicts = self._detect_philosophical_conflicts(all_suggestions)
        conflicts.extend(philosophical_conflicts)
        
        return conflicts
    
    def _analyze_line_conflict(self, line_num: int, line_suggestions: List[Tuple[CodeSuggestion, str]]) -> Optional[Conflict]:
        """Analyze conflict on a specific line"""
        
        suggestions = [s[0] for s in line_suggestions]
        agents = [s[1] for s in line_suggestions]
        
        # Check if suggestions are contradictory
        suggested_codes = [s.suggested_code for s in suggestions if s.suggested_code]
        
        if len(set(suggested_codes)) > 1:
            # Different code suggestions for same line
            conflict_type = ConflictType.CONTRADICTORY
            description = f"Multiple agents suggest different code changes for line {line_num}"
        elif len(suggested_codes) > 1:
            # Similar suggestions (overlapping)
            conflict_type = ConflictType.OVERLAPPING
            description = f"Multiple agents target the same issue on line {line_num}"
        else:
            return None
        
        impact = max(s.impact_score for s in suggestions)
        
        return Conflict(
            conflict_id=f"line_{line_num}_{hash(tuple(agents)) % 10000}",
            conflict_type=conflict_type,
            involved_agents=agents,
            conflicting_suggestions=suggestions,
            line_number=line_num,
            description=description,
            impact_assessment=impact
        )
    
    def _detect_philosophical_conflicts(self, all_suggestions: List[Tuple[CodeSuggestion, str]]) -> List[Conflict]:
        """Detect philosophical conflicts between different approaches"""
        
        conflicts = []
        
        # Common philosophical conflicts
        conflict_patterns = [
            {
                "name": "Performance vs Readability",
                "agents": ["Performance Agent", "Clean Code Agent"],
                "keywords": {
                    "performance": ["optimization", "efficiency", "speed", "inline", "loop"],
                    "readability": ["readable", "maintainable", "extract", "clear", "naming"]
                }
            },
            {
                "name": "Security vs Usability", 
                "agents": ["Security Agent", "Clean Code Agent"],
                "keywords": {
                    "security": ["validation", "sanitization", "encryption", "secure"],
                    "usability": ["simple", "user-friendly", "convenient"]
                }
            },
            {
                "name": "Abstraction vs Simplicity",
                "agents": ["Design Patterns Agent", "Clean Code Agent"],
                "keywords": {
                    "abstraction": ["pattern", "interface", "abstract", "polymorphism"],
                    "simplicity": ["simple", "straightforward", "direct"]
                }
            }
        ]
        
        for pattern in conflict_patterns:
            conflict = self._check_philosophical_pattern(all_suggestions, pattern)
            if conflict:
                conflicts.append(conflict)
        
        return conflicts
    
    def _check_philosophical_pattern(self, suggestions: List[Tuple[CodeSuggestion, str]], pattern: Dict) -> Optional[Conflict]:
        """Check for a specific philosophical conflict pattern"""
        
        involved_suggestions = []
        involved_agents = []
        
        for suggestion, agent_name in suggestions:
            if agent_name in pattern["agents"]:
                # Check if suggestion matches the philosophical keywords
                text = f"{suggestion.principle} {suggestion.reasoning} {suggestion.educational_explanation}".lower()
                
                for philosophy, keywords in pattern["keywords"].items():
                    if any(keyword in text for keyword in keywords):
                        involved_suggestions.append(suggestion)
                        involved_agents.append(agent_name)
                        break
        
        if len(set(involved_agents)) >= 2:  # At least 2 different agents involved
            return Conflict(
                conflict_id=f"philosophical_{pattern['name'].replace(' ', '_')}_{hash(tuple(involved_agents)) % 10000}",
                conflict_type=ConflictType.PHILOSOPHICAL,
                involved_agents=list(set(involved_agents)),
                conflicting_suggestions=involved_suggestions,
                line_number=None,
                description=f"Philosophical conflict: {pattern['name']}",
                impact_assessment=sum(s.impact_score for s in involved_suggestions) / len(involved_suggestions)
            )
        
        return None
    
    def _find_synergies(self, agent_results: List[AgentResult]) -> List[Synergy]:
        """Find synergistic suggestions that work better together"""
        
        synergies = []
        
        # Look for complementary security + performance suggestions
        security_suggestions = self._get_suggestions_by_agent(agent_results, "Security Agent")
        performance_suggestions = self._get_suggestions_by_agent(agent_results, "Performance Agent")
        
        synergy = self._find_security_performance_synergy(security_suggestions, performance_suggestions)
        if synergy:
            synergies.append(synergy)
        
        # Look for Clean Code + Design Patterns synergies
        clean_code_suggestions = self._get_suggestions_by_agent(agent_results, "Clean Code Agent")
        design_suggestions = self._get_suggestions_by_agent(agent_results, "Design Patterns Agent")
        
        synergy = self._find_design_clean_code_synergy(clean_code_suggestions, design_suggestions)
        if synergy:
            synergies.append(synergy)
        
        return synergies
    
    def _find_security_performance_synergy(self, security_suggestions: List[CodeSuggestion], 
                                         performance_suggestions: List[CodeSuggestion]) -> Optional[Synergy]:
        """Find synergies between security and performance suggestions"""
        
        # Look for input validation + caching opportunities
        validation_suggestions = [s for s in security_suggestions if "validation" in s.principle.lower()]
        caching_suggestions = [s for s in performance_suggestions if "caching" in s.reasoning.lower()]
        
        if validation_suggestions and caching_suggestions:
            combined_suggestions = validation_suggestions + caching_suggestions
            combined_impact = sum(s.impact_score for s in combined_suggestions) * 1.2  # Synergy bonus
            
            return Synergy(
                synergy_id=f"security_performance_{hash(tuple(s.id for s in combined_suggestions)) % 10000}",
                involved_agents=["Security Agent", "Performance Agent"],
                synergistic_suggestions=combined_suggestions,
                combined_impact=combined_impact,
                synthesis_description="Implement secure caching: validate inputs before caching to prevent cache poisoning while improving performance",
                implementation_order=["Implement input validation", "Add caching layer", "Combine for secure caching"]
            )
        
        return None
    
    def _find_design_clean_code_synergy(self, clean_code_suggestions: List[CodeSuggestion],
                                      design_suggestions: List[CodeSuggestion]) -> Optional[Synergy]:
        """Find synergies between design patterns and clean code suggestions"""
        
        # Look for SRP violations + Strategy pattern opportunities
        srp_suggestions = [s for s in clean_code_suggestions if "responsibility" in s.principle.lower()]
        strategy_suggestions = [s for s in design_suggestions if "strategy" in s.principle.lower()]
        
        if srp_suggestions and strategy_suggestions:
            combined_suggestions = srp_suggestions + strategy_suggestions
            combined_impact = sum(s.impact_score for s in combined_suggestions) * 1.15
            
            return Synergy(
                synergy_id=f"design_clean_{hash(tuple(s.id for s in combined_suggestions)) % 10000}",
                involved_agents=["Clean Code Agent", "Design Patterns Agent"],
                synergistic_suggestions=combined_suggestions,
                combined_impact=combined_impact,
                synthesis_description="Extract responsibilities into Strategy pattern: separate concerns while providing clean extensibility",
                implementation_order=["Identify responsibilities", "Extract strategies", "Implement pattern"]
            )
        
        return None
    
    def _get_suggestions_by_agent(self, agent_results: List[AgentResult], agent_name: str) -> List[CodeSuggestion]:
        """Get all suggestions from a specific agent"""
        for result in agent_results:
            if result.agent_name == agent_name:
                return result.suggestions
        return []
    
    def _resolve_single_conflict(self, conflict: Conflict) -> Conflict:
        """Resolve a single conflict using appropriate strategy"""
        
        # Choose resolution strategy based on conflict type and context
        strategy = self._choose_resolution_strategy(conflict)
        conflict.resolution_strategy = strategy
        
        if strategy == ResolutionStrategy.CONTEXT_DRIVEN:
            resolved = self._resolve_by_context(conflict)
        elif strategy == ResolutionStrategy.IMPACT_WEIGHTED:
            resolved = self._resolve_by_impact(conflict)
        elif strategy == ResolutionStrategy.AGENT_HIERARCHY:
            resolved = self._resolve_by_hierarchy(conflict)
        elif strategy == ResolutionStrategy.SYNTHESIS:
            resolved = self._resolve_by_synthesis(conflict)
        else:
            # Default to user choice
            resolved = self._prepare_for_user_choice(conflict)
        
        return resolved
    
    def _choose_resolution_strategy(self, conflict: Conflict) -> ResolutionStrategy:
        """Choose the best resolution strategy for a conflict"""
        
        if conflict.conflict_type == ConflictType.PHILOSOPHICAL:
            if self.project_context.priority != "balanced":
                return ResolutionStrategy.CONTEXT_DRIVEN
            else:
                return ResolutionStrategy.USER_CHOICE
        
        elif conflict.conflict_type == ConflictType.CONTRADICTORY:
            return ResolutionStrategy.IMPACT_WEIGHTED
        
        elif conflict.conflict_type == ConflictType.OVERLAPPING:
            return ResolutionStrategy.SYNTHESIS
        
        else:
            return ResolutionStrategy.AGENT_HIERARCHY
    
    def _resolve_by_context(self, conflict: Conflict) -> Conflict:
        """Resolve conflict based on project context"""
        
        context_priorities = {
            "performance": ["Performance Agent", "Security Agent", "Clean Code Agent"],
            "security": ["Security Agent", "Performance Agent", "Design Patterns Agent"],
            "maintainability": ["Clean Code Agent", "Design Patterns Agent", "Testability Agent"]
        }
        
        priority_order = context_priorities.get(self.project_context.priority, [])
        
        # Find the highest priority agent involved in the conflict
        for agent in priority_order:
            for suggestion in conflict.conflicting_suggestions:
                if suggestion.agent_name == agent:
                    conflict.resolved_suggestion = suggestion
                    conflict.resolution_rationale = f"Resolved based on project priority: {self.project_context.priority}"
                    break
            if conflict.resolved_suggestion:
                break
        
        if not conflict.resolved_suggestion:
            # Fallback to impact-based resolution
            return self._resolve_by_impact(conflict)
        
        return conflict
    
    def _resolve_by_impact(self, conflict: Conflict) -> Conflict:
        """Resolve conflict by choosing highest impact suggestion"""
        
        highest_impact_suggestion = max(conflict.conflicting_suggestions, key=lambda s: s.impact_score)
        
        conflict.resolved_suggestion = highest_impact_suggestion
        conflict.resolution_rationale = f"Resolved by selecting highest impact suggestion (score: {highest_impact_suggestion.impact_score})"
        
        return conflict
    
    def _resolve_by_hierarchy(self, conflict: Conflict) -> Conflict:
        """Resolve conflict using agent hierarchy"""
        
        # Find highest priority agent
        highest_priority = -1
        chosen_suggestion = None
        
        for suggestion in conflict.conflicting_suggestions:
            agent_priority = self.agent_hierarchy.get(suggestion.agent_name, 0)
            if agent_priority > highest_priority:
                highest_priority = agent_priority
                chosen_suggestion = suggestion
        
        conflict.resolved_suggestion = chosen_suggestion
        conflict.resolution_rationale = f"Resolved using agent hierarchy (priority: {highest_priority})"
        
        return conflict
    
    def _resolve_by_synthesis(self, conflict: Conflict) -> Conflict:
        """Resolve conflict by synthesizing suggestions"""
        
        # Create a combined suggestion that incorporates elements from all
        principles = [s.principle for s in conflict.conflicting_suggestions]
        reasonings = [s.reasoning for s in conflict.conflicting_suggestions]
        
        synthesized_suggestion = CodeSuggestion(
            id=f"synthesized_{conflict.conflict_id}",
            agent_name="Collaboration Engine",
            principle=f"Combined approach: {', '.join(set(principles))}",
            line_number=conflict.line_number,
            original_code=conflict.conflicting_suggestions[0].original_code,
            suggested_code=self._synthesize_code_suggestions(conflict.conflicting_suggestions),
            reasoning=f"Synthesized from multiple approaches: {'; '.join(reasonings)}",
            educational_explanation=self._synthesize_educational_explanations(conflict.conflicting_suggestions),
            impact_score=sum(s.impact_score for s in conflict.conflicting_suggestions) / len(conflict.conflicting_suggestions),
            confidence=min(s.confidence for s in conflict.conflicting_suggestions),
            severity=max(s.severity for s in conflict.conflicting_suggestions),
            category="synthesis"
        )
        
        conflict.resolved_suggestion = synthesized_suggestion
        conflict.resolution_rationale = "Resolved by synthesizing multiple agent suggestions into unified approach"
        
        return conflict
    
    def _synthesize_code_suggestions(self, suggestions: List[CodeSuggestion]) -> Optional[str]:
        """Synthesize code from multiple suggestions"""
        
        # Simple synthesis - prioritize suggestions with code
        code_suggestions = [s.suggested_code for s in suggestions if s.suggested_code]
        
        if code_suggestions:
            return code_suggestions[0]  # For now, take first one
        
        return None
    
    def _synthesize_educational_explanations(self, suggestions: List[CodeSuggestion]) -> str:
        """Synthesize educational explanations from multiple suggestions"""
        
        explanations = [s.educational_explanation for s in suggestions]
        return f"This represents a convergence of multiple best practices: {' | '.join(explanations)}"
    
    def _prepare_for_user_choice(self, conflict: Conflict) -> Conflict:
        """Prepare conflict for user resolution"""
        
        conflict.resolution_rationale = "Requires user decision - multiple valid approaches with different trade-offs"
        return conflict
    
    def _establish_priority_matrix(self, agent_results: List[AgentResult]) -> Dict[str, float]:
        """Establish priority matrix based on agent findings"""
        
        matrix = {}
        
        for result in agent_results:
            # Calculate priority score based on severity and quantity of issues
            critical_count = result.severity_breakdown.get('critical', 0)
            high_count = result.severity_breakdown.get('high', 0)
            medium_count = result.severity_breakdown.get('medium', 0)
            
            priority_score = (critical_count * 10 + high_count * 5 + medium_count * 2) / max(1, result.total_issues)
            matrix[result.agent_name] = priority_score
        
        return matrix
    
    def _recommend_focus_areas(self, agent_results: List[AgentResult], conflicts: List[Conflict], 
                              synergies: List[Synergy]) -> List[str]:
        """Recommend focus areas based on analysis"""
        
        focus_areas = []
        
        # High-priority issues
        for result in agent_results:
            critical_issues = result.severity_breakdown.get('critical', 0)
            high_issues = result.severity_breakdown.get('high', 0)
            
            if critical_issues > 0:
                focus_areas.append(f"{result.agent_name}: {critical_issues} critical issues require immediate attention")
            elif high_issues > 2:
                focus_areas.append(f"{result.agent_name}: Multiple high-impact improvements available")
        
        # Synergy opportunities
        for synergy in synergies:
            focus_areas.append(f"Synergy opportunity: {synergy.synthesis_description}")
        
        # Major conflicts needing resolution
        major_conflicts = [c for c in conflicts if c.impact_assessment > 7.0]
        if major_conflicts:
            focus_areas.append(f"Resolve {len(major_conflicts)} high-impact conflicts between agents")
        
        return focus_areas
    
    def _calculate_collaboration_score(self, conflicts: List[Conflict], synergies: List[Synergy], 
                                     total_suggestions: int) -> float:
        """Calculate overall collaboration effectiveness score (0-100)"""
        
        if total_suggestions == 0:
            return 100.0
        
        # Start with perfect score
        score = 100.0
        
        # Penalize conflicts
        conflict_penalty = len(conflicts) * 5
        major_conflict_penalty = len([c for c in conflicts if c.impact_assessment > 7.0]) * 10
        
        # Reward synergies
        synergy_bonus = len(synergies) * 10
        
        # Apply adjustments
        score = score - conflict_penalty - major_conflict_penalty + synergy_bonus
        
        # Ensure score is within valid range
        return max(0.0, min(100.0, score))


def create_default_project_context() -> ProjectContext:
    """Create default project context for testing"""
    return ProjectContext(
        priority="balanced",
        development_phase="development",
        team_size=5,
        performance_critical=False,
        security_sensitive=False,
        legacy_system=False,
        test_coverage=0.7,
        technical_debt_level="medium"
    )