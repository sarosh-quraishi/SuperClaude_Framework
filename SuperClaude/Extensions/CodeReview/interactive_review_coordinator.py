#!/usr/bin/env python3
"""
Interactive Review Coordinator
Integrates the InteractiveDiffReviewer with the existing CodeReview agent system
"""

import os
import sys
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import argparse
import tempfile
from datetime import datetime

from .agents import (
    AgentCoordinator, get_agent, get_all_agents, 
    CodeSuggestion, AgentResult, SeverityLevel
)
from .utils import (
    CodeParser, LanguageDetector, 
    InteractiveDiffReviewer, ReviewAction, ReviewDecision
)


class InteractiveReviewCoordinator:
    """Coordinates interactive reviews with the agent system"""
    
    def __init__(self, use_colors: bool = True, context_lines: int = 3):
        # Initialize with all available agents
        all_agents = get_all_agents()
        self.agent_coordinator = AgentCoordinator(all_agents)
        self.diff_reviewer = InteractiveDiffReviewer(use_colors, context_lines)
        self.code_parser = CodeParser()
        self.language_detector = LanguageDetector()
        
    def review_file(self, file_path: str, agents: Optional[List[str]] = None, 
                   **options) -> Dict[str, Any]:
        """Conduct interactive review of a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.review_code(content, file_path=file_path, agents=agents, **options)
    
    def review_code(self, code: str, file_path: Optional[str] = None, 
                   agents: Optional[List[str]] = None, **options) -> Dict[str, Any]:
        """Conduct interactive review of code content"""
        
        # Parse code (language detection is handled internally)
        code_context = self.code_parser.parse_code(code, file_path)
        
        # Get agent results
        agent_results = []
        if agents:
            # Use specific agents
            for agent_name in agents:
                agent = get_agent(agent_name)
                if agent:
                    # For now, create a mock result since we don't have real agent implementation
                    # In a real scenario, this would call agent.analyze_code(code_context)
                    result = self._create_mock_result(agent, code_context)
                    agent_results.append(result)
        else:
            # Use all agents
            all_agents = get_all_agents()
            for agent in all_agents:
                # For now, create mock results
                result = self._create_mock_result(agent, code_context)
                agent_results.append(result)
        
        # Collect all suggestions
        all_suggestions = []
        for result in agent_results:
            all_suggestions.extend(result.suggestions)
        
        # Filter by severity if specified
        if 'min_severity' in options:
            min_severity = SeverityLevel[options['min_severity'].upper()]
            all_suggestions = [s for s in all_suggestions 
                             if self._severity_meets_threshold(s.severity, min_severity)]
        
        # Sort suggestions by priority (severity, then impact)
        all_suggestions.sort(key=lambda s: (
            self._severity_priority(s.severity),
            -s.impact_score,
            s.line_number or 0
        ))
        
        # Conduct interactive review
        print(f"\n🔍 {self.diff_reviewer.colorize('Starting Interactive Code Review', 'bold')}")
        print(f"File: {file_path or 'Code Block'}")
        print(f"Language: {code_context.language.value}")
        print(f"Total suggestions: {len(all_suggestions)}")
        
        if not all_suggestions:
            print(f"{self.diff_reviewer.colorize('✅ No suggestions found - code looks good!', 'green')}")
            return {
                'decisions': [],
                'original_code': code,
                'final_code': code,
                'summary': {'total_suggestions': 0, 'accepted': 0, 'rejected': 0, 'skipped': 0}
            }
        
        # Start interactive review
        decisions = self.diff_reviewer.review_suggestions(
            all_suggestions, 
            file_path=file_path, 
            file_content=code
        )
        
        # Apply accepted changes
        final_code = self.diff_reviewer.apply_accepted_changes(all_suggestions)
        
        # Generate summary
        summary = self._generate_summary(decisions, all_suggestions)
        
        # Display results
        print("\n" + self.diff_reviewer.generate_review_summary())
        
        # Show changes if any were accepted
        accepted_count = len([d for d in decisions if d.action == ReviewAction.ACCEPT])
        if accepted_count > 0:
            print(f"\n{self.diff_reviewer.colorize('📝 Changes Applied:', 'bold')}")
            print(f"✅ {accepted_count} suggestions accepted and applied")
            
            if options.get('show_diff', True):
                self._show_final_diff(code, final_code)
        
        return {
            'decisions': decisions,
            'original_code': code,
            'final_code': final_code,
            'summary': summary,
            'agent_results': agent_results,
            'suggestions': all_suggestions
        }
    
    def review_directory(self, directory: str, pattern: str = "*", 
                        recursive: bool = True, **options) -> Dict[str, Any]:
        """Review multiple files in a directory"""
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find files to review
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        # Filter for supported file types
        supported_files = []
        for file_path in files:
            if file_path.is_file():
                language = self.language_detector.detect_from_file_path(str(file_path))
                if language.name != 'UNKNOWN':
                    supported_files.append(file_path)
        
        print(f"\n🔍 {self.diff_reviewer.colorize('Directory Review', 'bold')}")
        print(f"Directory: {directory}")
        print(f"Files found: {len(supported_files)}")
        
        if not supported_files:
            print(f"{self.diff_reviewer.colorize('❌ No supported files found', 'red')}")
            return {'files': [], 'summary': {}}
        
        # Review each file
        file_results = {}
        total_summary = {'files': 0, 'suggestions': 0, 'accepted': 0, 'rejected': 0, 'skipped': 0}
        
        for file_path in supported_files:
            print(f"\n{self.diff_reviewer.colorize(f'📁 Reviewing: {file_path.name}', 'cyan')}")
            
            try:
                result = self.review_file(str(file_path), **options)
                file_results[str(file_path)] = result
                
                # Update totals
                total_summary['files'] += 1
                total_summary['suggestions'] += result['summary']['total_suggestions']
                total_summary['accepted'] += result['summary']['accepted']
                total_summary['rejected'] += result['summary']['rejected']
                total_summary['skipped'] += result['summary']['skipped']
                
            except Exception as e:
                print(f"{self.diff_reviewer.colorize(f'❌ Error reviewing {file_path}: {e}', 'red')}")
                continue
        
        # Final summary
        print(f"\n{self.diff_reviewer.colorize('📊 Directory Review Complete', 'bold')}")
        print(f"Files reviewed: {total_summary['files']}")
        print(f"Total suggestions: {total_summary['suggestions']}")
        print(f"Accepted: {total_summary['accepted']}")
        print(f"Rejected: {total_summary['rejected']}")
        print(f"Skipped: {total_summary['skipped']}")
        
        return {
            'files': file_results,
            'summary': total_summary
        }
    
    def _create_mock_result(self, agent, code_context) -> 'AgentResult':
        """Create mock result for demonstration purposes"""
        from .agents import AgentResult
        import uuid
        
        # Create some sample suggestions based on the agent type
        suggestions = []
        
        agent_name = agent.__class__.__name__
        
        if "CleanCode" in agent_name:
            suggestions.append(CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name="Clean Code Agent",
                principle="Meaningful Names",
                line_number=1,
                original_code="def calc(x, y):",
                suggested_code="def calculate_sum(first_number, second_number):",
                reasoning="Function and parameter names should be descriptive and self-documenting",
                educational_explanation="Clean Code principle: Use intention-revealing names. Names should tell us why it exists, what it does, and how it is used.",
                impact_score=6.5,
                confidence=0.9,
                severity=SeverityLevel.MEDIUM,
                category="naming"
            ))
        
        elif "Security" in agent_name:
            suggestions.append(CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name="Security Agent",
                principle="Input Validation",
                line_number=5,
                original_code="user_input = input('Enter value: ')",
                suggested_code="user_input = input('Enter value: ').strip()[:100]  # Limit input length",
                reasoning="User input should be validated and sanitized to prevent injection attacks",
                educational_explanation="Security principle: Never trust user input. Always validate, sanitize, and limit input to prevent various injection attacks.",
                impact_score=8.0,
                confidence=0.85,
                severity=SeverityLevel.HIGH,
                category="input_validation"
            ))
        
        elif "Performance" in agent_name:
            suggestions.append(CodeSuggestion(
                id=str(uuid.uuid4()),
                agent_name="Performance Agent", 
                principle="Algorithm Optimization",
                line_number=10,
                original_code="for user in users:\n    if user.getAge() > 18:",
                suggested_code="adults = [user for user in users if user.age > 18]",
                reasoning="List comprehensions are more efficient than traditional loops for simple filtering",
                educational_explanation="Performance principle: List comprehensions are optimized at the C level and are generally faster than equivalent for loops.",
                impact_score=5.5,
                confidence=0.8,
                severity=SeverityLevel.LOW,
                category="algorithm"
            ))
        
        # Create severity breakdown
        severity_breakdown = {}
        for suggestion in suggestions:
            severity = suggestion.severity.value
            severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
        
        return AgentResult(
            agent_name=agent_name,
            agent_description=f"Mock {agent_name} for demonstration",
            suggestions=suggestions,
            total_issues=len(suggestions),
            execution_time=0.1,
            severity_breakdown=severity_breakdown
        )
    
    def save_session(self, results: Dict[str, Any], session_file: str) -> None:
        """Save review session to file"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'results': results
        }
        
        # Convert decisions to serializable format
        if 'decisions' in results:
            session_data['results']['decisions'] = [
                {
                    'suggestion_id': d.suggestion_id,
                    'action': d.action.value,
                    'modified_code': d.modified_code,
                    'timestamp': d.timestamp.isoformat(),
                    'reason': d.reason
                }
                for d in results['decisions']
            ]
        
        with open(session_file, 'w') as f:
            import json
            json.dump(session_data, f, indent=2)
        
        print(f"💾 Session saved to: {session_file}")
    
    def export_patch(self, original_code: str, final_code: str, patch_file: str) -> None:
        """Export changes as a patch file"""
        import difflib
        
        diff = difflib.unified_diff(
            original_code.splitlines(keepends=True),
            final_code.splitlines(keepends=True),
            fromfile='original',
            tofile='improved',
            lineterm=''
        )
        
        with open(patch_file, 'w') as f:
            f.writelines(diff)
        
        print(f"📄 Patch exported to: {patch_file}")
    
    def _severity_meets_threshold(self, severity: SeverityLevel, min_severity: SeverityLevel) -> bool:
        """Check if severity meets minimum threshold"""
        severity_order = {
            SeverityLevel.INFO: 0,
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        return severity_order[severity] >= severity_order[min_severity]
    
    def _severity_priority(self, severity: SeverityLevel) -> int:
        """Get priority order for sorting (lower number = higher priority)"""
        return {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
            SeverityLevel.INFO: 4
        }[severity]
    
    def _generate_summary(self, decisions: List[ReviewDecision], suggestions: List[CodeSuggestion]) -> Dict[str, int]:
        """Generate summary statistics"""
        action_counts = {}
        for decision in decisions:
            action_counts[decision.action] = action_counts.get(decision.action, 0) + 1
        
        return {
            'total_suggestions': len(suggestions),
            'accepted': action_counts.get(ReviewAction.ACCEPT, 0),
            'rejected': action_counts.get(ReviewAction.REJECT, 0),
            'skipped': action_counts.get(ReviewAction.SKIP, 0),
            'edited': len([d for d in decisions if d.modified_code is not None])
        }
    
    def _show_final_diff(self, original: str, final: str) -> None:
        """Show final diff of all changes"""
        import difflib
        
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            final.splitlines(keepends=True),
            fromfile='original',
            tofile='improved',
            lineterm=''
        ))
        
        if diff_lines:
            print(f"\n{self.diff_reviewer.colorize('📋 Final Diff:', 'bold')}")
            for line in diff_lines:
                if line.startswith('---') or line.startswith('+++'):
                    print(self.diff_reviewer.colorize(line.rstrip(), 'bold'))
                elif line.startswith('@@'):
                    print(self.diff_reviewer.colorize(line.rstrip(), 'cyan'))
                elif line.startswith('-'):
                    print(self.diff_reviewer.colorize(line.rstrip(), 'red'))
                elif line.startswith('+'):
                    print(self.diff_reviewer.colorize(line.rstrip(), 'green'))
                else:
                    print(line.rstrip())


def create_cli_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser for interactive review"""
    parser = argparse.ArgumentParser(
        description="Interactive Code Review with Diff-Style Feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'target', 
        help='File path, directory, or code snippet to review'
    )
    
    parser.add_argument(
        '--agent', '-a',
        choices=['clean_code', 'security', 'performance', 'design_patterns', 'testability'],
        action='append',
        help='Specific agent(s) to use for review'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Process directories recursively'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        default='*',
        help='File pattern for directory processing (default: *)'
    )
    
    parser.add_argument(
        '--min-severity',
        choices=['info', 'low', 'medium', 'high', 'critical'],
        default='info',
        help='Minimum severity level to show (default: info)'
    )
    
    parser.add_argument(
        '--context', '-c',
        type=int,
        default=3,
        help='Number of context lines in diff (default: 3)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--save-session',
        help='Save review session to JSON file'
    )
    
    parser.add_argument(
        '--export-patch',
        help='Export final changes as patch file'
    )
    
    parser.add_argument(
        '--code',
        action='store_true',
        help='Treat target as code snippet instead of file path'
    )
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Create coordinator
    coordinator = InteractiveReviewCoordinator(
        use_colors=not args.no_color,
        context_lines=args.context
    )
    
    try:
        if args.code:
            # Review code snippet
            results = coordinator.review_code(
                args.target,
                agents=args.agent,
                min_severity=args.min_severity
            )
        elif os.path.isfile(args.target):
            # Review single file
            results = coordinator.review_file(
                args.target,
                agents=args.agent,
                min_severity=args.min_severity
            )
        elif os.path.isdir(args.target):
            # Review directory
            results = coordinator.review_directory(
                args.target,
                pattern=args.pattern,
                recursive=args.recursive,
                min_severity=args.min_severity
            )
        else:
            print(f"❌ Target not found: {args.target}")
            return 1
        
        # Save session if requested
        if args.save_session:
            coordinator.save_session(results, args.save_session)
        
        # Export patch if requested
        if args.export_patch and 'original_code' in results and 'final_code' in results:
            coordinator.export_patch(
                results['original_code'],
                results['final_code'],
                args.export_patch
            )
        
        print(f"\n✅ {coordinator.diff_reviewer.colorize('Interactive review complete!', 'green')}")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ {coordinator.diff_reviewer.colorize('Review interrupted by user', 'yellow')}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())