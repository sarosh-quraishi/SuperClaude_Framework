#!/usr/bin/env python3
"""
/sc:clean_code_level_0 Command Implementation

Quick Clean Code analysis using Crew AI agent for immediate feedback.
Part of the two-pass Clean Code analysis system.
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipelines.clean_code_pipeline import CleanCodePipeline

# Constants
JSON_INDENT_SPACES = 2

async def sc_clean_code_level_0(code_input: str, **kwargs) -> Dict[str, Any]:
    """
    Execute Clean Code Level 0 analysis
    
    Args:
        code_input: Code to analyze (file path or code string)
        **kwargs: Additional options
        
    Returns:
        dict: Analysis results from Level 0 agent
    """
    pipeline = CleanCodePipeline()
    
    # Determine if input is file path or code string
    code, filename = _parse_code_input(code_input)
    
    # Run only Level 0 analysis
    language = pipeline.detect_language(code, filename)
    level_0_results = await pipeline.run_level_0_analysis(code, language)
    
    return {
        "results": level_0_results,
        "metadata": {
            "command": "sc:clean_code_level_0",
            "language": language,
            "filename": filename
        }
    }

def _parse_code_input(code_input: str) -> Tuple[str, Optional[str]]:
    """Parse input to determine if it's a file path or code string.
    
    Args:
        code_input: Input that could be a file path or code string
        
    Returns:
        Tuple of (code_content, filename_or_none)
    """
    if Path(code_input).exists():
        with open(code_input, 'r') as f:
            code = f.read()
        return code, code_input
    else:
        return code_input, None

def _display_human_readable_output(results: Dict[str, Any]) -> None:
    """Display analysis results in human-readable format.
    
    Args:
        results: Analysis results to display
    """
    analysis = results["results"]
    
    print(f"🔍 Clean Code Level 0 Analysis")
    print(f"Language: {results['metadata']['language']}")
    print(f"Total Issues: {analysis['analysis_summary']['total_issues']}")
    print(f"High Priority: {analysis['analysis_summary']['high_priority']}")
    print(f"Medium Priority: {analysis['analysis_summary']['medium_priority']}")
    print(f"Low Priority: {analysis['analysis_summary']['low_priority']}")
    
    if analysis['issues']:
        print("\n📋 Issues Found:")
        for issue in analysis['issues']:
            print(f"  {issue['severity'].upper()}: {issue['issue_title']} (Line {issue['line_number']})")
            print(f"    Principle: {issue['clean_code_principle']}")
            print(f"    Fix: {issue['recommendation']}")
            print()
    
    if analysis['quick_wins']:
        print("🚀 Quick Wins:")
        for win in analysis['quick_wins']:
            print(f"  • {win}")

def main():
    """CLI wrapper for the command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Code Level 0 - Quick Analysis")
    parser.add_argument("input", help="File path or code string to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        results = asyncio.run(sc_clean_code_level_0(args.input))
        
        if args.json:
            print(json.dumps(results, indent=JSON_INDENT_SPACES))
        else:
            _display_human_readable_output(results)
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()