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
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipelines.clean_code_pipeline import CleanCodePipeline

async def sc_clean_code(code_input: str, **kwargs) -> dict:
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
    if Path(code_input).exists():
        with open(code_input, 'r') as f:
            code = f.read()
        filename = code_input
    else:
        code = code_input
        filename = None
    
    # Run complete analysis
    results = await pipeline.analyze_code(code, filename)
    
    # Save report if output file specified
    if kwargs.get('output_file'):
        output_format = kwargs.get('format', 'markdown')
        
        if output_format == 'json':
            content = json.dumps(results, indent=2)
        else:
            content = results['final_report']
        
        with open(kwargs['output_file'], 'w') as f:
            f.write(content)
        
        print(f"📄 Report saved to: {kwargs['output_file']}")
    
    return results

def main():
    """CLI wrapper for the complete command"""
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
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", 
                       help="Output format (default: markdown)")
    parser.add_argument("--json", action="store_true", help="Output as JSON (shortcut for --format json)")
    parser.add_argument("--level0-only", action="store_true", help="Run only Level 0 analysis")
    parser.add_argument("--level1-only", action="store_true", help="Run only Level 1 analysis (requires Level 0 results)")
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input and not args.code:
        parser.error("Must provide either a file path or --code option")
    
    code_input = args.code if args.code else args.input
    
    # Set format
    output_format = "json" if args.json else args.format
    
    try:
        if args.level0_only:
            # Run only Level 0
            from SuperClaude.Commands.sc_clean_code_level_0 import sc_clean_code_level_0
            results = asyncio.run(sc_clean_code_level_0(code_input))
            
            if output_format == "json":
                output = json.dumps(results, indent=2)
            else:
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
                
        elif args.level1_only:
            # Run only Level 1 (user must provide Level 0 results separately)
            print("❌ Level 1 only mode requires Level 0 results. Use the complete pipeline instead.")
            sys.exit(1)
            
        else:
            # Run complete two-pass analysis
            results = asyncio.run(sc_clean_code(
                code_input,
                output_file=args.output,
                format=output_format
            ))
            
            if output_format == "json":
                output = json.dumps(results, indent=2)
            else:
                output = results["final_report"]
        
        # Display or save output
        if args.output:
            # Already saved in sc_clean_code function
            pass
        else:
            print("\n" + "="*60)
            print("CLEAN CODE ANALYSIS RESULTS")
            print("="*60)
            print(output)
        
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