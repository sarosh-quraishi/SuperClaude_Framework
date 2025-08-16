#!/usr/bin/env python3
"""
Interactive Diff-Style Review Interface
Provides Git-like diff visualization with accept/reject options for code suggestions
"""

import os
import sys
import difflib
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from ..agents import CodeSuggestion, AgentResult, SeverityLevel


class ReviewAction(Enum):
    """Available actions for review suggestions"""
    ACCEPT = "accept"
    REJECT = "reject"
    SKIP = "skip"
    EDIT = "edit"
    LEARN_MORE = "learn_more"
    ACCEPT_ALL = "accept_all"
    REJECT_ALL = "reject_all"


@dataclass
class DiffHunk:
    """Represents a diff hunk with context"""
    original_lines: List[str]
    suggested_lines: List[str]
    start_line: int
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)
    suggestion: Optional[CodeSuggestion] = None


@dataclass
class ReviewDecision:
    """Stores user decision for a suggestion"""
    suggestion_id: str
    action: ReviewAction
    modified_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None


class InteractiveDiffReviewer:
    """Interactive diff-style code review interface"""
    
    # ANSI color codes for diff display
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m'
    }
    
    # Diff line prefixes
    DIFF_SYMBOLS = {
        'context': ' ',
        'remove': '-',
        'add': '+',
        'hunk_header': '@',
        'file_header': '+++'
    }
    
    def __init__(self, use_colors: bool = True, context_lines: int = 3):
        self.use_colors = use_colors and self._supports_color()
        self.context_lines = context_lines
        self.decisions: List[ReviewDecision] = []
        self.current_file_content: List[str] = []
        self.modified_content: List[str] = []
        
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return (
            hasattr(sys.stdout, 'isatty') and 
            sys.stdout.isatty() and 
            os.environ.get('TERM') != 'dumb'
        )
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def create_diff_hunk(self, suggestion: CodeSuggestion, file_lines: List[str]) -> DiffHunk:
        """Create a diff hunk from a suggestion"""
        start_line = max(0, (suggestion.line_number or 1) - 1)
        
        # Extract original code lines
        if suggestion.original_code:
            original_lines = suggestion.original_code.strip().split('\n')
        else:
            # Estimate affected lines
            original_lines = file_lines[start_line:start_line + 1]
        
        # Get suggested code lines
        suggested_lines = []
        if suggestion.suggested_code:
            suggested_lines = suggestion.suggested_code.strip().split('\n')
        
        # Add context lines
        context_before = file_lines[max(0, start_line - self.context_lines):start_line]
        end_line = min(len(file_lines), start_line + len(original_lines))
        context_after = file_lines[end_line:end_line + self.context_lines]
        
        return DiffHunk(
            original_lines=original_lines,
            suggested_lines=suggested_lines,
            start_line=start_line,
            context_before=context_before,
            context_after=context_after,
            suggestion=suggestion
        )
    
    def format_diff_hunk(self, hunk: DiffHunk) -> str:
        """Format diff hunk in Git-style format"""
        diff_lines = []
        
        # Hunk header
        original_count = len(hunk.original_lines)
        suggested_count = len(hunk.suggested_lines)
        context_start = hunk.start_line - len(hunk.context_before) + 1
        
        header = f"@@ -{context_start},{original_count + len(hunk.context_before) + len(hunk.context_after)} "
        header += f"+{context_start},{suggested_count + len(hunk.context_before) + len(hunk.context_after)} @@"
        
        if hunk.suggestion:
            header += f" {hunk.suggestion.principle}"
        
        diff_lines.append(self.colorize(header, 'cyan'))
        
        # Context before
        for line in hunk.context_before:
            diff_lines.append(f"{self.DIFF_SYMBOLS['context']}{line}")
        
        # Removed lines
        for line in hunk.original_lines:
            colored_line = self.colorize(f"{self.DIFF_SYMBOLS['remove']}{line}", 'red')
            diff_lines.append(colored_line)
        
        # Added lines
        for line in hunk.suggested_lines:
            colored_line = self.colorize(f"{self.DIFF_SYMBOLS['add']}{line}", 'green')
            diff_lines.append(colored_line)
        
        # Context after
        for line in hunk.context_after:
            diff_lines.append(f"{self.DIFF_SYMBOLS['context']}{line}")
        
        return '\n'.join(diff_lines)
    
    def format_suggestion_header(self, suggestion: CodeSuggestion) -> str:
        """Format suggestion header with metadata"""
        severity_colors = {
            SeverityLevel.CRITICAL: 'bg_red',
            SeverityLevel.HIGH: 'red',
            SeverityLevel.MEDIUM: 'yellow',
            SeverityLevel.LOW: 'blue',
            SeverityLevel.INFO: 'cyan'
        }
        
        severity_color = severity_colors.get(suggestion.severity, 'white')
        
        header = f"\n{'=' * 80}\n"
        header += f"🔍 {self.colorize(suggestion.agent_name, 'bold')} | "
        header += f"{self.colorize(suggestion.severity.value.upper(), severity_color)} | "
        header += f"Line {suggestion.line_number or 'N/A'}\n"
        header += f"{'=' * 80}\n"
        
        # Principle and reasoning
        header += f"\n📋 {self.colorize('Principle:', 'bold')} {suggestion.principle}\n"
        header += f"💡 {self.colorize('Why:', 'bold')} {suggestion.reasoning}\n"
        
        # Metrics
        header += f"\n📊 Impact: {suggestion.impact_score}/10 | "
        header += f"Confidence: {suggestion.confidence:.0%}\n"
        
        return header
    
    def format_educational_info(self, suggestion: CodeSuggestion) -> str:
        """Format educational explanation"""
        if not suggestion.educational_explanation:
            return ""
        
        info = f"\n{self.colorize('📚 Educational Context:', 'blue')}\n"
        info += f"{suggestion.educational_explanation}\n"
        return info
    
    def display_suggestion_diff(self, suggestion: CodeSuggestion, file_lines: List[str]) -> None:
        """Display a single suggestion as an interactive diff"""
        # Clear screen for better focus
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Show header
        print(self.format_suggestion_header(suggestion))
        
        # Show educational info if requested
        print(self.format_educational_info(suggestion))
        
        # Show diff
        hunk = self.create_diff_hunk(suggestion, file_lines)
        print(f"\n{self.colorize('Diff:', 'bold')}")
        print(self.format_diff_hunk(hunk))
        
        # Show available actions
        print(f"\n{self.colorize('Available Actions:', 'bold')}")
        actions = [
            f"{self.colorize('[a]', 'green')} Accept",
            f"{self.colorize('[r]', 'red')} Reject", 
            f"{self.colorize('[s]', 'yellow')} Skip",
            f"{self.colorize('[e]', 'blue')} Edit",
            f"{self.colorize('[l]', 'cyan')} Learn More",
            f"{self.colorize('[A]', 'green')} Accept All",
            f"{self.colorize('[R]', 'red')} Reject All",
            f"{self.colorize('[q]', 'magenta')} Quit"
        ]
        print(" | ".join(actions))
    
    def get_user_input(self, suggestion: CodeSuggestion) -> ReviewAction:
        """Get user input for review decision"""
        while True:
            try:
                choice = input(f"\n{self.colorize('Your choice:', 'bold')} ").strip().lower()
                
                action_map = {
                    'a': ReviewAction.ACCEPT,
                    'r': ReviewAction.REJECT,
                    's': ReviewAction.SKIP,
                    'e': ReviewAction.EDIT,
                    'l': ReviewAction.LEARN_MORE,
                    'A': ReviewAction.ACCEPT_ALL,
                    'R': ReviewAction.REJECT_ALL,
                    'q': None  # Quit
                }
                
                if choice == 'q':
                    return None
                elif choice in action_map:
                    return action_map[choice]
                else:
                    print(f"{self.colorize('Invalid choice. Please try again.', 'red')}")
                    
            except KeyboardInterrupt:
                print(f"\n{self.colorize('Review interrupted by user.', 'yellow')}")
                return None
            except EOFError:
                return None
    
    def handle_edit_action(self, suggestion: CodeSuggestion) -> Optional[str]:
        """Handle edit action by opening editor"""
        try:
            # Create temporary file with suggested code
            suggested_code = suggestion.suggested_code or suggestion.original_code or ""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False) as f:
                f.write(suggested_code)
                temp_file = f.name
            
            # Open editor
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor, temp_file])
            
            # Read modified content
            with open(temp_file, 'r') as f:
                modified_code = f.read().strip()
            
            # Cleanup
            os.unlink(temp_file)
            
            return modified_code
            
        except Exception as e:
            print(f"{self.colorize(f'Error opening editor: {e}', 'red')}")
            return None
    
    def show_learn_more(self, suggestion: CodeSuggestion) -> None:
        """Show detailed educational information"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"{self.colorize('📚 Detailed Learning Information', 'bold')}")
        print("=" * 80)
        
        print(f"\n{self.colorize('Agent:', 'bold')} {suggestion.agent_name}")
        print(f"{self.colorize('Principle:', 'bold')} {suggestion.principle}")
        print(f"{self.colorize('Severity:', 'bold')} {suggestion.severity.value}")
        
        print(f"\n{self.colorize('Detailed Explanation:', 'blue')}")
        print(suggestion.educational_explanation or "No detailed explanation available.")
        
        if suggestion.original_code:
            print(f"\n{self.colorize('Current Code:', 'red')}")
            print(f"```\n{suggestion.original_code}\n```")
        
        if suggestion.suggested_code:
            print(f"\n{self.colorize('Suggested Improvement:', 'green')}")
            print(f"```\n{suggestion.suggested_code}\n```")
        
        print(f"\n{self.colorize('Why This Matters:', 'yellow')}")
        print(suggestion.reasoning)
        
        input(f"\n{self.colorize('Press Enter to continue...', 'dim')}")
    
    def review_suggestions(self, suggestions: List[CodeSuggestion], file_path: str = None, 
                          file_content: str = None) -> List[ReviewDecision]:
        """Conduct interactive review of suggestions"""
        if file_content:
            self.current_file_content = file_content.split('\n')
        elif file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.current_file_content = f.read().split('\n')
        else:
            self.current_file_content = []
        
        self.modified_content = self.current_file_content.copy()
        
        print(f"{self.colorize('🔍 Interactive Code Review Started', 'bold')}")
        print(f"Total suggestions: {len(suggestions)}")
        
        if file_path:
            print(f"File: {file_path}")
        
        print(f"\n{self.colorize('Navigation Tips:', 'cyan')}")
        print("- Use 'a' to accept, 'r' to reject, 's' to skip")
        print("- Use 'l' for detailed explanations")
        print("- Use 'e' to edit suggestions manually")
        print("- Use 'A'/'R' for batch accept/reject")
        print("- Use 'q' to quit review")
        
        input(f"\n{self.colorize('Press Enter to start review...', 'dim')}")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{self.colorize(f'Reviewing suggestion {i}/{len(suggestions)}', 'bold')}")
            
            # Display suggestion
            self.display_suggestion_diff(suggestion, self.current_file_content)
            
            # Get user decision
            action = self.get_user_input(suggestion)
            
            if action is None:  # Quit
                break
            elif action == ReviewAction.LEARN_MORE:
                self.show_learn_more(suggestion)
                # Redisplay and get new action
                self.display_suggestion_diff(suggestion, self.current_file_content)
                action = self.get_user_input(suggestion)
                if action is None:
                    break
            
            # Handle edit action
            modified_code = None
            if action == ReviewAction.EDIT:
                modified_code = self.handle_edit_action(suggestion)
                if modified_code is not None:
                    action = ReviewAction.ACCEPT  # Treat edited as accepted
            
            # Record decision
            decision = ReviewDecision(
                suggestion_id=f"{suggestion.agent_name}_{suggestion.line_number}_{i}",
                action=action,
                modified_code=modified_code
            )
            self.decisions.append(decision)
            
            # Handle batch actions
            if action == ReviewAction.ACCEPT_ALL:
                # Accept remaining suggestions
                for remaining_suggestion in suggestions[i:]:
                    remaining_decision = ReviewDecision(
                        suggestion_id=f"{remaining_suggestion.agent_name}_{remaining_suggestion.line_number}_{i}",
                        action=ReviewAction.ACCEPT
                    )
                    self.decisions.append(remaining_decision)
                break
            elif action == ReviewAction.REJECT_ALL:
                # Reject remaining suggestions
                for remaining_suggestion in suggestions[i:]:
                    remaining_decision = ReviewDecision(
                        suggestion_id=f"{remaining_suggestion.agent_name}_{remaining_suggestion.line_number}_{i}",
                        action=ReviewAction.REJECT
                    )
                    self.decisions.append(remaining_decision)
                break
        
        return self.decisions
    
    def apply_accepted_changes(self, suggestions: List[CodeSuggestion]) -> str:
        """Apply accepted changes to generate final code"""
        if not self.current_file_content:
            return ""
        
        result_lines = self.current_file_content.copy()
        
        # Get accepted decisions
        accepted_decisions = [d for d in self.decisions if d.action == ReviewAction.ACCEPT]
        
        # Sort by line number (descending) to avoid offset issues
        suggestion_map = {f"{s.agent_name}_{s.line_number}_{i+1}": s 
                         for i, s in enumerate(suggestions)}
        
        accepted_suggestions = []
        for decision in accepted_decisions:
            if decision.suggestion_id in suggestion_map:
                suggestion = suggestion_map[decision.suggestion_id]
                suggestion._modified_code = decision.modified_code  # Store custom edits
                accepted_suggestions.append(suggestion)
        
        # Sort by line number (descending)
        accepted_suggestions.sort(key=lambda s: s.line_number or 0, reverse=True)
        
        # Apply changes
        for suggestion in accepted_suggestions:
            line_num = (suggestion.line_number or 1) - 1
            
            if suggestion._modified_code:
                # Use custom edited code
                new_lines = suggestion._modified_code.split('\n')
            elif suggestion.suggested_code:
                # Use agent's suggested code
                new_lines = suggestion.suggested_code.split('\n')
            else:
                continue
            
            # Replace the lines
            if line_num < len(result_lines):
                # Determine how many lines to replace
                if suggestion.original_code:
                    lines_to_replace = len(suggestion.original_code.split('\n'))
                else:
                    lines_to_replace = 1
                
                # Replace the lines
                result_lines[line_num:line_num + lines_to_replace] = new_lines
        
        return '\n'.join(result_lines)
    
    def generate_review_summary(self) -> str:
        """Generate summary of review session"""
        if not self.decisions:
            return "No decisions made during review."
        
        action_counts = {}
        for decision in self.decisions:
            action_counts[decision.action] = action_counts.get(decision.action, 0) + 1
        
        summary = f"{self.colorize('📊 Review Summary', 'bold')}\n"
        summary += "=" * 50 + "\n"
        
        for action, count in action_counts.items():
            color = {'ACCEPT': 'green', 'REJECT': 'red', 'SKIP': 'yellow'}.get(action.name, 'white')
            summary += f"{action.value.title()}: {self.colorize(str(count), color)}\n"
        
        summary += f"\nTotal decisions: {len(self.decisions)}\n"
        
        return summary
    
    def save_review_session(self, file_path: str) -> None:
        """Save review session to JSON file"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'decisions': [
                {
                    'suggestion_id': d.suggestion_id,
                    'action': d.action.value,
                    'modified_code': d.modified_code,
                    'timestamp': d.timestamp.isoformat(),
                    'reason': d.reason
                }
                for d in self.decisions
            ],
            'summary': {
                'total_decisions': len(self.decisions),
                'accepted': len([d for d in self.decisions if d.action == ReviewAction.ACCEPT]),
                'rejected': len([d for d in self.decisions if d.action == ReviewAction.REJECT]),
                'skipped': len([d for d in self.decisions if d.action == ReviewAction.SKIP])
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(session_data, f, indent=2)


def quick_review_demo():
    """Quick demonstration of the interactive diff reviewer"""
    # Sample suggestion for demo
    sample_suggestion = CodeSuggestion(
        agent_name="Clean Code Agent",
        principle="Meaningful Names",
        line_number=5,
        original_code="def calc(x, y):\n    return x + y",
        suggested_code="def calculate_sum(first_number, second_number):\n    return first_number + second_number",
        reasoning="Function and parameter names should be descriptive and self-documenting",
        educational_explanation="Clean Code principle: Use intention-revealing names. Names should tell us why it exists, what it does, and how it is used.",
        severity=SeverityLevel.MEDIUM,
        impact_score=6.5,
        confidence=0.9
    )
    
    # Sample file content
    sample_code = """# Simple calculator
def main():
    print("Calculator Demo")
    
def calc(x, y):
    return x + y
    
def multiply(a, b):
    return a * b
    
if __name__ == "__main__":
    main()
"""
    
    # Create reviewer and demonstrate
    reviewer = InteractiveDiffReviewer()
    decisions = reviewer.review_suggestions([sample_suggestion], file_content=sample_code)
    
    print("\n" + reviewer.generate_review_summary())
    
    # Show final result if changes were accepted
    accepted_decisions = [d for d in decisions if d.action == ReviewAction.ACCEPT]
    if accepted_decisions:
        final_code = reviewer.apply_accepted_changes([sample_suggestion])
        print(f"\n{reviewer.colorize('Final Code:', 'bold')}")
        print(final_code)


if __name__ == "__main__":
    quick_review_demo()