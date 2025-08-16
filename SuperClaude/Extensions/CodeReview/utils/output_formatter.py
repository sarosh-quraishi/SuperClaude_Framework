#!/usr/bin/env python3
"""
Output Formatter for Multi-Agent Code Review System
Handles different output formats: interactive, report, and JSON
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from ..agents import AgentResult, CodeSuggestion, SeverityLevel


@dataclass
class ReviewSession:
    """Represents a complete code review session"""
    session_id: str
    timestamp: datetime
    file_path: Optional[str]
    original_code: str
    language: str
    agent_results: List[AgentResult]
    conflicts: List[Dict[str, Any]]
    summary: Dict[str, Any]


class InteractiveFormatter:
    """Formats output for interactive CLI display"""
    
    # ANSI color codes
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }
    
    # Agent color mapping
    AGENT_COLORS = {
        'Clean Code Agent': 'blue',
        'Security Agent': 'red',
        'Performance Agent': 'yellow',
        'Design Patterns Agent': 'purple',
        'Testability Agent': 'green'
    }
    
    # Severity icons and colors
    SEVERITY_DISPLAY = {
        SeverityLevel.CRITICAL: ('🚨', 'red'),
        SeverityLevel.HIGH: ('⚠️', 'yellow'),
        SeverityLevel.MEDIUM: ('💡', 'cyan'),
        SeverityLevel.LOW: ('ℹ️', 'white'),
        SeverityLevel.INFO: ('📋', 'white')
    }
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def format_header(self, title: str, subtitle: str = "") -> str:
        """Format section header"""
        header = self.colorize(f"\n{'═' * 60}", 'cyan')
        header += f"\n{self.colorize(title, 'bold')}"
        if subtitle:
            header += f"\n{self.colorize(subtitle, 'white')}"
        header += f"\n{self.colorize('═' * 60, 'cyan')}\n"
        return header
    
    def format_suggestion_card(self, suggestion: CodeSuggestion) -> str:
        """Format individual suggestion as interactive card"""
        severity_icon, severity_color = self.SEVERITY_DISPLAY[suggestion.severity]
        agent_color = self.AGENT_COLORS.get(suggestion.agent_name, 'white')
        
        # Header with severity and agent
        header = f"\n{severity_icon} {self.colorize(suggestion.severity.value.upper(), severity_color)}: {suggestion.principle}"
        header += f"\n📍 Line {suggestion.line_number or 'N/A'}"
        
        # Agent information
        agent_line = f"┌─ {self.colorize(suggestion.agent_name, agent_color)} "
        agent_line += "─" * (60 - len(suggestion.agent_name) - 3) + "┐"
        
        card = f"{header}\n{agent_line}\n│"
        
        # Current code (if available)
        if suggestion.original_code:
            card += f"\n│ {self.colorize('❌ Current Code:', 'red')}"
            for line in suggestion.original_code.split('\n'):
                card += f"\n│    {line}"
            card += "\n│"
        
        # Suggested improvement (if available)
        if suggestion.suggested_code:
            card += f"\n│ {self.colorize('✅ Suggested Improvement:', 'green')}"
            for line in suggestion.suggested_code.split('\n'):
                card += f"\n│    {line}"
            card += "\n│"
        
        # Reasoning
        card += f"\n│ {self.colorize('💡 Why This Matters:', 'cyan')}"
        card += f"\n│    {self._wrap_text(suggestion.reasoning, 56)}"
        card += "\n│"
        
        # Educational explanation
        card += f"\n│ {self.colorize('📚 Educational Explanation:', 'blue')}"
        card += f"\n│    {self._wrap_text(suggestion.educational_explanation, 56)}"
        card += "\n│"
        
        # Metrics
        card += f"\n│ {self.colorize('📊 Metrics:', 'yellow')}"
        card += f"\n│    Impact: {suggestion.impact_score}/10 | Confidence: {suggestion.confidence:.0%}"
        card += "\n│"
        
        # Action buttons
        card += f"\n│ {self.colorize('[ Accept ]', 'green')} {self.colorize('[ Reject ]', 'red')} {self.colorize('[ Learn More ]', 'blue')}"
        
        # Footer
        card += f"\n└{'─' * 59}┘"
        
        return card
    
    def format_conflict(self, conflict: Dict[str, Any]) -> str:
        """Format agent conflict information"""
        header = f"\n⚠️ {self.colorize('Methodology Conflict Detected', 'yellow')}\n"
        
        conflict_info = f"📍 {conflict.get('issue', 'Conflicting recommendations')}\n"
        conflict_info += f"🤖 Agents: {', '.join(conflict.get('agents', []))}\n"
        
        if 'suggestions' in conflict:
            for i, suggestion in enumerate(conflict['suggestions'], 1):
                agent_color = self.AGENT_COLORS.get(suggestion.get('agent_name', ''), 'white')
                conflict_info += f"\n{i}. {self.colorize(suggestion.get('agent_name', 'Unknown'), agent_color)}:"
                conflict_info += f"\n   {suggestion.get('reasoning', 'No reasoning provided')}\n"
        
        resolution = "\n🎯 Resolution Recommendation:\n"
        resolution += "   Consider project context and priorities to resolve this conflict.\n"
        resolution += "   Both approaches may be valid depending on requirements.\n"
        
        return header + conflict_info + resolution
    
    def format_summary(self, session: ReviewSession) -> str:
        """Format comprehensive review summary"""
        summary = self.format_header("🎯 Multi-Agent Code Review Summary")
        
        # Overall assessment
        summary += "📊 Overall Assessment:\n"
        for result in session.agent_results:
            agent_color = self.AGENT_COLORS.get(result.agent_name, 'white')
            agent_icon = self._get_agent_icon(result.agent_name)
            summary += f"├── {agent_icon} {self.colorize(result.agent_name, agent_color)}: "
            summary += f"{result.total_issues} suggestions\n"
        
        # Priority actions
        critical_suggestions = self._get_critical_suggestions(session.agent_results)
        if critical_suggestions:
            summary += f"\n🚨 {self.colorize('Priority Actions (Fix Immediately):', 'red')}\n"
            for i, suggestion in enumerate(critical_suggestions[:5], 1):
                summary += f"{i}. {suggestion.agent_name}: {suggestion.principle} "
                summary += f"(Line {suggestion.line_number or 'N/A'})\n"
        
        # High-impact improvements
        high_impact = self._get_high_impact_suggestions(session.agent_results)
        if high_impact:
            summary += f"\n💡 {self.colorize('High-Impact Improvements:', 'yellow')}\n"
            for i, suggestion in enumerate(high_impact[:5], 1):
                summary += f"{i}. {suggestion.agent_name}: {suggestion.principle}\n"
        
        # Learning insights
        summary += f"\n📚 {self.colorize('Learning Insights:', 'blue')}\n"
        insights = self._generate_learning_insights(session.agent_results)
        for insight in insights:
            summary += f"├── {insight}\n"
        
        # Conflicts
        if session.conflicts:
            summary += f"\n⚖️ {self.colorize(f'Methodology Conflicts Detected: {len(session.conflicts)}', 'yellow')}\n"
            for conflict in session.conflicts[:3]:
                summary += f"├── {conflict.get('issue', 'Conflict detected')}\n"
        
        return summary
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(current_line) <= width:
                current_line.append(word)
                current_length += len(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n│    '.join(lines)
    
    def _get_agent_icon(self, agent_name: str) -> str:
        """Get emoji icon for agent"""
        icons = {
            'Clean Code Agent': '🧹',
            'Security Agent': '🛡️',
            'Performance Agent': '⚡',
            'Design Patterns Agent': '🏗️',
            'Testability Agent': '🧪'
        }
        return icons.get(agent_name, '🤖')
    
    def _get_critical_suggestions(self, results: List[AgentResult]) -> List[CodeSuggestion]:
        """Get critical and high severity suggestions"""
        critical = []
        for result in results:
            for suggestion in result.suggestions:
                if suggestion.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                    critical.append(suggestion)
        
        return sorted(critical, key=lambda s: (s.severity.value, -s.impact_score))
    
    def _get_high_impact_suggestions(self, results: List[AgentResult]) -> List[CodeSuggestion]:
        """Get high-impact suggestions"""
        high_impact = []
        for result in results:
            for suggestion in result.suggestions:
                if suggestion.impact_score >= 7.0:
                    high_impact.append(suggestion)
        
        return sorted(high_impact, key=lambda s: -s.impact_score)
    
    def _generate_learning_insights(self, results: List[AgentResult]) -> List[str]:
        """Generate learning insights from agent results"""
        insights = []
        
        # Security insights
        security_results = [r for r in results if r.agent_name == 'Security Agent']
        if security_results and security_results[0].total_issues > 0:
            insights.append("Security: Code contains potential vulnerabilities - prioritize input validation and secure coding practices")
        
        # Performance insights
        performance_results = [r for r in results if r.agent_name == 'Performance Agent']
        if performance_results and performance_results[0].total_issues > 0:
            insights.append("Performance: Algorithm choices impact scalability - consider data structure optimization")
        
        # Clean Code insights
        clean_code_results = [r for r in results if r.agent_name == 'Clean Code Agent']
        if clean_code_results and clean_code_results[0].total_issues > 0:
            insights.append("Clean Code: Focus on meaningful names and function decomposition for better maintainability")
        
        # Design patterns insights
        design_results = [r for r in results if r.agent_name == 'Design Patterns Agent']
        if design_results and design_results[0].total_issues > 0:
            insights.append("Architecture: SOLID principles violations detected - consider dependency injection and single responsibility")
        
        # Testability insights
        test_results = [r for r in results if r.agent_name == 'Testability Agent']
        if test_results and test_results[0].total_issues > 0:
            insights.append("Testing: Hard-coded dependencies make testing difficult - implement dependency injection")
        
        return insights


class ReportFormatter:
    """Formats output as comprehensive report"""
    
    def format_comprehensive_report(self, session: ReviewSession) -> str:
        """Generate detailed report format"""
        report = f"""
# Multi-Agent Code Review Report

## Session Information
- **Session ID**: {session.session_id}
- **Timestamp**: {session.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **File**: {session.file_path or 'Code Block'}
- **Language**: {session.language}

## Executive Summary

"""
        
        # Summary statistics
        total_suggestions = sum(result.total_issues for result in session.agent_results)
        report += f"- **Total Suggestions**: {total_suggestions}\n"
        report += f"- **Agents Analyzed**: {len(session.agent_results)}\n"
        report += f"- **Conflicts Detected**: {len(session.conflicts)}\n\n"
        
        # Agent breakdown
        report += "### Agent Analysis Breakdown\n\n"
        for result in session.agent_results:
            report += f"- **{result.agent_name}**: {result.total_issues} suggestions "
            report += f"(Execution time: {result.execution_time:.2f}s)\n"
        
        # Detailed findings
        report += "\n## Detailed Findings\n\n"
        
        for result in session.agent_results:
            if result.suggestions:
                report += f"### {result.agent_name}\n\n"
                report += f"{result.agent_description}\n\n"
                
                for suggestion in result.suggestions:
                    report += f"#### {suggestion.principle}\n\n"
                    report += f"**Location**: Line {suggestion.line_number or 'N/A'}\n"
                    report += f"**Severity**: {suggestion.severity.value}\n"
                    report += f"**Impact Score**: {suggestion.impact_score}/10\n"
                    report += f"**Confidence**: {suggestion.confidence:.0%}\n\n"
                    
                    if suggestion.original_code:
                        report += "**Current Code:**\n```\n"
                        report += suggestion.original_code + "\n```\n\n"
                    
                    if suggestion.suggested_code:
                        report += "**Suggested Code:**\n```\n"
                        report += suggestion.suggested_code + "\n```\n\n"
                    
                    report += f"**Reasoning**: {suggestion.reasoning}\n\n"
                    report += f"**Educational Explanation**: {suggestion.educational_explanation}\n\n"
                    report += "---\n\n"
        
        # Conflicts section
        if session.conflicts:
            report += "## Methodology Conflicts\n\n"
            for i, conflict in enumerate(session.conflicts, 1):
                report += f"### Conflict {i}: {conflict.get('issue', 'Conflict detected')}\n\n"
                report += f"**Agents Involved**: {', '.join(conflict.get('agents', []))}\n\n"
                report += "**Resolution Needed**: Manual review required to resolve conflicting recommendations.\n\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        report += "### Priority Order\n\n"
        
        critical_suggestions = self._get_critical_suggestions_for_report(session.agent_results)
        for i, suggestion in enumerate(critical_suggestions[:10], 1):
            report += f"{i}. **{suggestion.principle}** ({suggestion.agent_name})\n"
            report += f"   - Severity: {suggestion.severity.value}\n"
            report += f"   - Impact: {suggestion.impact_score}/10\n\n"
        
        return report
    
    def _get_critical_suggestions_for_report(self, results: List[AgentResult]) -> List[CodeSuggestion]:
        """Get suggestions ordered by priority for report"""
        all_suggestions = []
        for result in results:
            all_suggestions.extend(result.suggestions)
        
        # Sort by severity first, then impact score
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 4
        }
        
        return sorted(all_suggestions, 
                     key=lambda s: (severity_order[s.severity], -s.impact_score))


class JSONFormatter:
    """Formats output as structured JSON"""
    
    def format_json(self, session: ReviewSession) -> str:
        """Convert session to JSON format"""
        # Convert session to dictionary
        session_dict = {
            'session_id': session.session_id,
            'timestamp': session.timestamp.isoformat(),
            'file_path': session.file_path,
            'language': session.language,
            'summary': session.summary,
            'agent_results': [result.to_dict() for result in session.agent_results],
            'conflicts': session.conflicts,
            'metadata': {
                'total_suggestions': sum(result.total_issues for result in session.agent_results),
                'total_agents': len(session.agent_results),
                'total_conflicts': len(session.conflicts)
            }
        }
        
        return json.dumps(session_dict, indent=2, ensure_ascii=False)


class OutputManager:
    """Manages different output formats"""
    
    def __init__(self):
        self.interactive_formatter = InteractiveFormatter()
        self.report_formatter = ReportFormatter()
        self.json_formatter = JSONFormatter()
    
    def format_output(self, session: ReviewSession, format_type: str = 'interactive') -> str:
        """Format output according to specified type"""
        if format_type == 'interactive':
            return self._format_interactive(session)
        elif format_type == 'report':
            return self.report_formatter.format_comprehensive_report(session)
        elif format_type == 'json':
            return self.json_formatter.format_json(session)
        else:
            raise ValueError(f"Unknown format type: {format_type}")
    
    def _format_interactive(self, session: ReviewSession) -> str:
        """Format for interactive display"""
        output = self.interactive_formatter.format_header(
            "🤖 Multi-Agent Code Review Results",
            f"File: {session.file_path or 'Code Block'} | Language: {session.language}"
        )
        
        # Show suggestions by agent
        for result in session.agent_results:
            if result.suggestions:
                agent_header = f"\n{self.interactive_formatter._get_agent_icon(result.agent_name)} "
                agent_header += f"{result.agent_name} Analysis"
                output += self.interactive_formatter.format_header(agent_header)
                
                for suggestion in result.suggestions:
                    output += self.interactive_formatter.format_suggestion_card(suggestion)
        
        # Show conflicts
        if session.conflicts:
            output += self.interactive_formatter.format_header("⚖️ Methodology Conflicts")
            for conflict in session.conflicts:
                output += self.interactive_formatter.format_conflict(conflict)
        
        # Show summary
        output += self.interactive_formatter.format_summary(session)
        
        return output