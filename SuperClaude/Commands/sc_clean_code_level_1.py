#!/usr/bin/env python3
"""
/sc:clean_code_level_1 Command Implementation

Deep Clean Code analysis using RAG-powered agent with Clean Code book citations.
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

async def sc_clean_code_level_1(code_input: str, level_0_results: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Execute Clean Code Level 1 analysis
    
    Args:
        code_input: Code to analyze (file path or code string)
        level_0_results: Results from Level 0 analysis (optional, will run Level 0 if not provided)
        **kwargs: Additional options
        
    Returns:
        dict: Analysis results from Level 1 agent with citations
    """
    pipeline = CleanCodePipeline()
    
    # Determine if input is file path or code string
    code, filename = _parse_code_input(code_input)
    
    language = pipeline.detect_language(code, filename)
    
    # If no Level 0 results provided, run Level 0 first
    if level_0_results is None:
        print("ℹ️  Running Level 0 analysis first...")
        level_0_results = await pipeline.run_level_0_analysis(code, language)
    
    # Run Level 1 analysis
    level_1_results = await pipeline.run_level_1_analysis(code, language, level_0_results)
    
    return {
        "level_0_results": level_0_results,
        "level_1_results": level_1_results,
        "metadata": {
            "command": "sc:clean_code_level_1",
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

def _load_level_0_results(results_file_path: str) -> Optional[Dict[str, Any]]:
    """Load Level 0 results from JSON file.
    
    Args:
        results_file_path: Path to JSON file with Level 0 results
        
    Returns:
        Level 0 results dictionary or None if file doesn't exist
    """
    if not results_file_path:
        return None
        
    with open(results_file_path, 'r') as f:
        level_0_data = json.load(f)
        return level_0_data.get('results', level_0_data)

def _display_citations_only(level_1_results: Dict[str, Any]) -> None:
    """Display only book citations from Level 1 results.
    
    Args:
        level_1_results: Level 1 analysis results
    """
    if "detailed_issues" not in level_1_results:
        return
        
    print("📚 Clean Code Book Citations\n")
    for issue in level_1_results["detailed_issues"]:
        print(f"Issue: {issue['level_0_issue_id']}")
        for citation in issue["deep_analysis"]["book_citations"]:
            print(f"  📖 {citation['chapter']} - {citation['section']}")
            print(f"      Pages: {citation['page_range']}")
            print(f"      Quote: \"{citation['key_quote']}\"")
            print(f"      Relevance: {citation['relevance']}")
            print()

def _display_human_readable_output(results: Dict[str, Any]) -> None:
    """Display Level 1 results in human-readable format.
    
    Args:
        results: Complete Level 1 analysis results
    """
    level_1 = results["level_1_results"]
    print(f"📚 Clean Code Level 1 Deep Analysis")
    print(f"Language: {results['metadata']['language']}")
    
    if "message" in level_1:
        print(f"\n{level_1['message']}")
        return
    
    print(f"Issues Analyzed: {level_1['deep_analysis']['total_issues_analyzed']}")
    print(f"Book Sections Referenced: {', '.join(level_1['deep_analysis']['book_sections_referenced'])}")
    
    print("\n📖 Deep Analysis with Citations:")
    for issue in level_1["detailed_issues"]:
        print(f"\n🔍 {issue['level_0_issue_id']}:")
        
        # Show citations
        for citation in issue["deep_analysis"]["book_citations"]:
            print(f"  📚 {citation['chapter']} - {citation['section']} (p.{citation['page_range']})")
            print(f"     \"{citation['key_quote']}\"")
        
        # Show enhanced recommendation
        enhanced = issue["enhanced_recommendation"]
        print(f"  🎯 Immediate Action: {enhanced['immediate_action']}")
        print(f"  📚 Study: {', '.join(enhanced['learning_resources'])}")
    
    # Show synthesis
    synthesis = level_1["synthesis"]
    print(f"\n🎯 Overall Assessment: {synthesis['overall_code_health']}")
    print(f"📚 Priority Study Areas:")
    for rec in synthesis["book_study_recommendations"]:
        print(f"  • {rec['chapter']} - {rec['reason']} (Priority: {rec['study_priority']})")

def main():
    """CLI wrapper for the command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Code Level 1 - Deep Analysis with Citations")
    parser.add_argument("input", help="File path or code string to analyze")
    parser.add_argument("--level0-results", help="JSON file with Level 0 results (optional)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--citations-only", action="store_true", help="Show only citations and quotes")
    
    args = parser.parse_args()
    
    try:
        level_0_results = _load_level_0_results(args.level0_results)
        results = asyncio.run(sc_clean_code_level_1(args.input, level_0_results))
        
        if args.json:
            print(json.dumps(results, indent=JSON_INDENT_SPACES))
        elif args.citations_only:
            _display_citations_only(results["level_1_results"])
        else:
            _display_human_readable_output(results)
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()