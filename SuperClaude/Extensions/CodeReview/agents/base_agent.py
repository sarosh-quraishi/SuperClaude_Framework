#!/usr/bin/env python3
"""
Base Agent Class for SuperClaude Multi-Agent Code Review System
Educational AI code review with specialized domain expertise
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import re
import uuid


class SeverityLevel(Enum):
    """Severity levels for code review suggestions"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CodeSuggestion:
    """Represents a single code review suggestion from an agent"""
    id: str
    agent_name: str
    principle: str
    line_number: Optional[int]
    original_code: Optional[str]
    suggested_code: Optional[str]
    reasoning: str
    educational_explanation: str
    impact_score: float  # 1-10 scale
    confidence: float    # 0-1 scale
    severity: SeverityLevel
    category: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "principle": self.principle,
            "line_number": self.line_number,
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "reasoning": self.reasoning,
            "educational_explanation": self.educational_explanation,
            "impact_score": self.impact_score,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "category": self.category
        }


@dataclass
class AgentResult:
    """Complete analysis result from a single agent"""
    agent_name: str
    agent_description: str
    suggestions: List[CodeSuggestion]
    execution_time: float
    total_issues: int
    severity_breakdown: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "agent_name": self.agent_name,
            "agent_description": self.agent_description,
            "suggestions": [s.to_dict() for s in self.suggestions],
            "execution_time": self.execution_time,
            "total_issues": self.total_issues,
            "severity_breakdown": self.severity_breakdown
        }


class BaseAgent(ABC):
    """Abstract base class for all code review agents"""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.system_prompt = self.get_system_prompt()
        self.specializations = self.get_specializations()
        
    @abstractmethod
    def get_name(self) -> str:
        """Return the agent's name"""
        pass
        
    @abstractmethod 
    def get_description(self) -> str:
        """Return the agent's description"""
        pass
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
        
    @abstractmethod
    def get_specializations(self) -> List[str]:
        """Return list of this agent's specializations"""
        pass
        
    @abstractmethod
    def get_analysis_prompt(self, code: str, language: str, file_path: Optional[str] = None) -> str:
        """Generate analysis prompt for the given code"""
        pass
        
    async def analyze_code(self, code: str, language: str, file_path: Optional[str] = None) -> AgentResult:
        """
        Analyze code and return structured results
        This method coordinates the analysis process
        """
        import time
        start_time = time.time()
        
        # Generate analysis prompt
        analysis_prompt = self.get_analysis_prompt(code, language, file_path)
        
        # Perform analysis (this would call Claude API in real implementation)
        suggestions = await self._perform_analysis(analysis_prompt, code, language)
        
        # Calculate metrics
        execution_time = time.time() - start_time
        total_issues = len(suggestions)
        severity_breakdown = self._calculate_severity_breakdown(suggestions)
        
        return AgentResult(
            agent_name=self.name,
            agent_description=self.description,
            suggestions=suggestions,
            execution_time=execution_time,
            total_issues=total_issues,
            severity_breakdown=severity_breakdown
        )
    
    async def _perform_analysis(self, prompt: str, code: str, language: str) -> List[CodeSuggestion]:
        """
        Perform the actual analysis using Claude API
        This is a placeholder - real implementation would call Claude
        """
        # In a real implementation, this would:
        # 1. Call Claude API with the prompt
        # 2. Parse the structured JSON response
        # 3. Validate and create CodeSuggestion objects
        
        # For demonstration, return empty list
        # Real implementation would parse Claude's response
        return self._mock_analysis(code, language)
    
    def _mock_analysis(self, code: str, language: str) -> List[CodeSuggestion]:
        """Generate mock suggestions for testing purposes"""
        suggestions = []
        lines = code.split('\n')
        
        # Basic pattern matching for demo purposes
        for i, line in enumerate(lines, 1):
            if self._should_analyze_line(line):
                suggestion = self._create_mock_suggestion(line, i, language)
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _should_analyze_line(self, line: str) -> bool:
        """Determine if a line should be analyzed (override in subclasses)"""
        return len(line.strip()) > 0
    
    def _create_mock_suggestion(self, line: str, line_number: int, language: str) -> Optional[CodeSuggestion]:
        """Create a mock suggestion (override in subclasses)"""
        return None
    
    def _calculate_severity_breakdown(self, suggestions: List[CodeSuggestion]) -> Dict[str, int]:
        """Calculate breakdown of suggestions by severity"""
        breakdown = {severity.value: 0 for severity in SeverityLevel}
        for suggestion in suggestions:
            breakdown[suggestion.severity.value] += 1
        return breakdown
    
    def validate_suggestion(self, suggestion_data: Dict[str, Any]) -> Optional[CodeSuggestion]:
        """Validate and create CodeSuggestion from parsed data"""
        try:
            # Validate required fields
            required_fields = ['principle', 'reasoning', 'educational_explanation', 'impact_score', 'confidence']
            for field in required_fields:
                if field not in suggestion_data:
                    return None
            
            # Create CodeSuggestion with validation
            return CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name=self.name,
                principle=suggestion_data['principle'],
                line_number=suggestion_data.get('line_number'),
                original_code=suggestion_data.get('original_code'),
                suggested_code=suggestion_data.get('suggested_code'),
                reasoning=suggestion_data['reasoning'],
                educational_explanation=suggestion_data['educational_explanation'],
                impact_score=max(1.0, min(10.0, float(suggestion_data['impact_score']))),
                confidence=max(0.0, min(1.0, float(suggestion_data['confidence']))),
                severity=self._determine_severity(suggestion_data['impact_score']),
                category=suggestion_data.get('category', 'general')
            )
        except (ValueError, KeyError, TypeError):
            return None
    
    def _determine_severity(self, impact_score: float) -> SeverityLevel:
        """Determine severity level based on impact score"""
        if impact_score >= 9.0:
            return SeverityLevel.CRITICAL
        elif impact_score >= 7.0:
            return SeverityLevel.HIGH
        elif impact_score >= 5.0:
            return SeverityLevel.MEDIUM
        elif impact_score >= 3.0:
            return SeverityLevel.LOW
        else:
            return SeverityLevel.INFO
    
    def get_json_response_format(self) -> str:
        """Return the expected JSON response format for Claude"""
        return """
        Respond with a JSON array of suggestions in this exact format:
        [
          {
            "principle": "Name of the principle/rule being applied",
            "line_number": 10,
            "original_code": "exact code to change (optional)",
            "suggested_code": "improved version (optional)",
            "reasoning": "Why this violates the principle",
            "educational_explanation": "Teaching explanation for developers",
            "impact_score": 7.5,
            "confidence": 0.9,
            "category": "naming|structure|security|performance|testing|other"
          }
        ]
        
        Important:
        - impact_score: 1-10 (10 = critical issue, 1 = minor suggestion)
        - confidence: 0-1 (1 = completely certain, 0 = uncertain)
        - Only include suggestions that genuinely improve the code
        - Focus on educational value - explain WHY the change matters
        """


class AgentCoordinator:
    """Coordinates multiple agents for comprehensive code review"""
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
    
    async def run_comprehensive_review(self, code: str, language: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Run all agents in parallel and compile results"""
        import asyncio
        
        # Run all agents in parallel
        tasks = [agent.analyze_code(code, language, file_path) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        
        # Compile comprehensive report
        return self._compile_comprehensive_report(results, code)
    
    def _compile_comprehensive_report(self, results: List[AgentResult], original_code: str) -> Dict[str, Any]:
        """Compile results from all agents into comprehensive report"""
        all_suggestions = []
        agent_summaries = []
        
        for result in results:
            all_suggestions.extend(result.suggestions)
            agent_summaries.append({
                "name": result.agent_name,
                "total_issues": result.total_issues,
                "execution_time": result.execution_time,
                "severity_breakdown": result.severity_breakdown
            })
        
        # Detect conflicts between agents
        conflicts = self._detect_conflicts(results)
        
        # Calculate overall metrics
        total_suggestions = len(all_suggestions)
        avg_impact = sum(s.impact_score for s in all_suggestions) / max(1, total_suggestions)
        
        return {
            "summary": {
                "total_agents": len(self.agents),
                "total_suggestions": total_suggestions,
                "average_impact_score": avg_impact,
                "conflicts_detected": len(conflicts)
            },
            "agent_results": [result.to_dict() for result in results],
            "agent_summaries": agent_summaries,
            "conflicts": conflicts,
            "all_suggestions": [s.to_dict() for s in all_suggestions],
            "original_code": original_code
        }
    
    def _detect_conflicts(self, results: List[AgentResult]) -> List[Dict[str, Any]]:
        """Detect conflicts between different agent recommendations"""
        conflicts = []
        
        # Group suggestions by line number
        suggestions_by_line = {}
        for result in results:
            for suggestion in result.suggestions:
                if suggestion.line_number:
                    line = suggestion.line_number
                    if line not in suggestions_by_line:
                        suggestions_by_line[line] = []
                    suggestions_by_line[line].append((result.agent_name, suggestion))
        
        # Check for conflicting suggestions on the same line
        for line_num, line_suggestions in suggestions_by_line.items():
            if len(line_suggestions) > 1:
                # Check if suggestions conflict
                suggested_codes = [s[1].suggested_code for s in line_suggestions if s[1].suggested_code]
                if len(set(suggested_codes)) > 1:  # Different suggestions for same line
                    conflicts.append({
                        "type": "line_conflict",
                        "line_number": line_num,
                        "agents": [s[0] for s in line_suggestions],
                        "issue": f"Multiple agents suggest different changes for line {line_num}",
                        "suggestions": [s[1].to_dict() for s in line_suggestions]
                    })
        
        return conflicts