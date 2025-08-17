#!/usr/bin/env python3
"""
/sc:clean_code Command Implementation

Complete two-pass Clean Code analysis orchestrating Level 0 and Level 1 agents.
Generates comprehensive Markdown report with quick feedback and citations.
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
OUTPUT_SEPARATOR_LENGTH = 60
OUTPUT_SEPARATOR_CHAR = "="
FORMAT_JSON = "json"
FORMAT_MARKDOWN = "markdown"

async def sc_clean_code(code_input: str, **kwargs) -> Dict[str, Any]:
    """
    Execute complete two-pass Clean Code analysis
    
    Args:
        code_input: Code to analyze (file path or code string)
        **kwargs: Additional options (output_file, format, etc.)
        
    Returns:
        dict: Complete analysis results with final report
    """
    pipeline = CleanCodePipeline()
    
    # Determine if input is file path or code string
    code, filename = _parse_code_input(code_input)
    
    # Run complete analysis
    results = await pipeline.analyze_code(code, filename)
    
    # Save report if output file specified
    if kwargs.get('output_file'):
        _save_analysis_report(results, kwargs)
    
    return results

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

def _save_analysis_report(results: Dict[str, Any], options: Dict[str, Any]) -> None:
    """Save analysis report to specified output file.
    
    Args:
        results: Complete analysis results
        options: Output options including format and file path
    """
    output_format = options.get('format', 'markdown')
    
    if output_format == 'json':
        content = json.dumps(results, indent=2)
    else:
        content = results['final_report']
    
    with open(options['output_file'], 'w') as f:
        f.write(content)
    
    print(f"📄 Report saved to: {options['output_file']}")

def _create_argument_parser() -> 'argparse.ArgumentParser':
    """Create and configure the command line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean Code Two-Pass Analysis - Complete Review with Citations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m SuperClaude.Commands.sc_clean_code my_code.py
  python -m SuperClaude.Commands.sc_clean_code --code "def calc(x,y): return x+y"
  python -m SuperClaude.Commands.sc_clean_code my_code.py --output report.md
  python -m SuperClaude.Commands.sc_clean_code my_code.py --format json --output results.json
        """
    )
    
    parser.add_argument("input", nargs="?", help="File path to analyze")
    parser.add_argument("--code", help="Code string to analyze directly")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--format", choices=[FORMAT_MARKDOWN, FORMAT_JSON], default=FORMAT_MARKDOWN, 
                       help="Output format (default: markdown)")
    parser.add_argument("--json", action="store_true", help="Output as JSON (shortcut for --format json)")
    parser.add_argument("--level0-only", action="store_true", help="Run only Level 0 analysis")
    parser.add_argument("--level1-only", action="store_true", help="Run only Level 1 analysis (requires Level 0 results)")
    
    return parser

def _validate_input_arguments(args) -> str:
    """Validate and extract code input from arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Code input string (file path or code content)
        
    Raises:
        SystemExit: If validation fails
    """
    if not args.input and not args.code:
        print("❌ Error: Must provide either a file path or --code option")
        sys.exit(1)
    
    return args.code if args.code else args.input

def _determine_output_format(args) -> str:
    """Determine output format from arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Output format string
    """
    return FORMAT_JSON if args.json else args.format

def _execute_level_0_only(code_input: str, output_format: str) -> str:
    """Execute Level 0 only analysis.
    
    Args:
        code_input: Code to analyze
        output_format: Output format (json or markdown)
        
    Returns:
        Formatted output string
    """
    from SuperClaude.Commands.sc_clean_code_level_0 import sc_clean_code_level_0
    results = asyncio.run(sc_clean_code_level_0(code_input))
    
    if output_format == FORMAT_JSON:
        return json.dumps(results, indent=2)
    else:
        return _format_level_0_markdown_output(results)

def _format_level_0_markdown_output(results: Dict[str, Any]) -> str:
    """Format Level 0 results as markdown.
    
    Args:
        results: Level 0 analysis results
        
    Returns:
        Formatted markdown string
    """
    analysis = results["results"]
    output = f"""# Clean Code Level 0 Analysis

**Total Issues:** {analysis['analysis_summary']['total_issues']}
**Language:** {results['metadata']['language']}

## Issues Found:
"""
    
    for issue in analysis['issues']:
        output += f"""
### {issue['severity'].upper()}: {issue['issue_title']} (Line {issue['line_number']})
**Principle:** {issue['clean_code_principle']}
**Recommendation:** {issue['recommendation']}
"""
    
    return output

def _execute_complete_analysis(code_input: str, output_file: Optional[str], output_format: str) -> str:
    """Execute complete two-pass analysis.
    
    Args:
        code_input: Code to analyze
        output_file: Optional output file path
        output_format: Output format (json or markdown)
        
    Returns:
        Formatted output string
    """
    results = asyncio.run(sc_clean_code(
        code_input,
        output_file=output_file,
        format=output_format
    ))
    
    if output_format == FORMAT_JSON:
        return json.dumps(results, indent=2)
    else:
        return results["final_report"]

def _display_output_with_header(output: str) -> None:
    """Display output with formatted header.
    
    Args:
        output: Content to display
    """
    separator = OUTPUT_SEPARATOR_CHAR * OUTPUT_SEPARATOR_LENGTH
    print(f"\n{separator}")
    print("CLEAN CODE ANALYSIS RESULTS")
    print(separator)
    print(output)

def main():
    """CLI wrapper for the complete command"""
    parser = _create_argument_parser()
    args = parser.parse_args()
    
    code_input = _validate_input_arguments(args)
    output_format = _determine_output_format(args)
    
    try:
        if args.level0_only:
            output = _execute_level_0_only(code_input, output_format)
        elif args.level1_only:
            print("❌ Level 1 only mode requires Level 0 results. Use the complete pipeline instead.")
            sys.exit(1)
        else:
            output = _execute_complete_analysis(code_input, args.output, output_format)
        
        # Display or save output
        if not args.output:
            _display_output_with_header(output)
        
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()