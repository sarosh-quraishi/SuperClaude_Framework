#!/usr/bin/env python3
"""
Clean Code Two-Pass Analysis Pipeline

Orchestrates Level 0 (quick Crew AI analysis) and Level 1 (RAG-powered deep analysis)
to provide comprehensive Clean Code feedback with citations.

Usage:
    python -m pipelines.clean_code_pipeline --file path/to/code.py
    python -m pipelines.clean_code_pipeline --code "def calc(x,y): return x+y"
"""

import json
import yaml
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CleanCodePipeline:
    """Two-pass Clean Code analysis orchestrator"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or str(project_root / "agents" / "clean_code")
        self.level_0_config = self._load_agent_config("clean_code_level_0.yaml")
        self.level_1_config = self._load_agent_config("clean_code_level_1.yaml")
        
    def _load_agent_config(self, filename: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file"""
        config_path = Path(self.config_dir) / filename
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Agent config not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filename}: {e}")
    
    def detect_language(self, code: str, filename: str = None) -> str:
        """Detect programming language from code or filename"""
        if filename:
            ext = Path(filename).suffix.lower()
            ext_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.java': 'java', '.go': 'go', '.cpp': 'cpp', '.c': 'c',
                '.cs': 'csharp', '.rb': 'ruby', '.php': 'php'
            }
            if ext in ext_map:
                return ext_map[ext]
        
        # Simple heuristics for language detection
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code or 'const ' in code:
            return 'javascript'
        elif 'public class ' in code or 'private ' in code:
            return 'java'
        elif 'func ' in code and 'package ' in code:
            return 'go'
        
        return 'unknown'
    
    def _generate_meaningful_fix(self, line: str, var: str) -> str:
        """Generate a meaningful variable name suggestion based on context"""
        line_lower = line.lower()
        
        # Context-based suggestions with word boundary protection
        if 'for' in line_lower and 'range' in line_lower:
            if 'len(' in line_lower:
                if 'user' in line_lower or 'data' in line_lower:
                    new_var = 'item_index'
                else:
                    new_var = 'index'
            else:
                new_var = 'counter'
        elif 'user' in line_lower:
            new_var = 'user_record'
        elif 'data' in line_lower:
            new_var = 'processed_data'
        elif 'file' in line_lower:
            new_var = 'file_content'
        elif 'result' in line_lower:
            new_var = 'calculation_result'
        elif 'temp' in line_lower:
            new_var = 'temporary_value'
        elif '+' in line or '*' in line or '/' in line:
            new_var = 'calculated_value'
        else:
            new_var = f'meaningful_{var}_name'
        
        # Replace only whole word occurrences to avoid partial replacements
        import re
        pattern = r'\b' + re.escape(var) + r'\b'
        return re.sub(pattern, new_var, line)
    
    async def run_level_0_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Run Level 0 quick analysis using Crew AI agent"""
        print("🔍 Running Level 0 Analysis (Quick Clean Code Review)...")
        
        # In a real implementation, this would use Crew AI
        # For now, we'll simulate the analysis based on the prompt
        level_0_result = await self._simulate_level_0_analysis(code, language)
        
        print(f"✅ Level 0 Complete: Found {level_0_result['analysis_summary']['total_issues']} issues")
        return level_0_result
    
    async def run_level_1_analysis(self, code: str, language: str, level_0_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run Level 1 deep analysis using RAG-powered agent"""
        if level_0_results['analysis_summary']['total_issues'] == 0:
            print("ℹ️  Skipping Level 1 Analysis - no issues found in Level 0")
            return {"message": "No issues requiring deep analysis"}
        
        print("📚 Running Level 1 Analysis (RAG-Powered Deep Review)...")
        
        # In a real implementation, this would use RAG with Clean Code book
        level_1_result = await self._simulate_level_1_analysis(code, language, level_0_results)
        
        print(f"✅ Level 1 Complete: Analyzed {level_1_result['deep_analysis']['total_issues_analyzed']} issues with book citations")
        return level_1_result
    
    async def _simulate_level_0_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """Simulate Level 0 analysis (replace with actual Crew AI implementation)"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        issues = []
        issue_id = 1
        
        # Analyze for common Clean Code violations
        lines = code.split('\n')
        
        # Check for short variable names
        for i, line in enumerate(lines, 1):
            for var in ['x', 'y', 'a', 'b', 'i', 'j']:
                if f' {var} ' in line or f' {var}=' in line:
                    issues.append({
                        "id": f"CC{issue_id:03d}",
                        "category": "naming",
                        "severity": "medium",
                        "line_number": i,
                        "code_snippet": line.strip(),
                        "issue_title": "Non-descriptive variable names",
                        "description": f"Variable '{var}' doesn't reveal intention",
                        "clean_code_principle": "Use Intention-Revealing Names (Chapter 2)",
                        "recommendation": f"Rename '{var}' to describe what it represents",
                        "example_fix": self._generate_meaningful_fix(line, var),
                        "impact": "Reduces code readability and makes maintenance harder",
                        "effort_to_fix": "low"
                    })
                    issue_id += 1
                    break  # Only flag one variable per line
        
        # Check for function length (simple heuristic)
        function_lines = 0
        in_function = False
        function_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def ') or line.strip().startswith('function '):
                in_function = True
                function_start = i
                function_lines = 1
            elif in_function and line.strip():
                function_lines += 1
            elif in_function and not line.strip() and i > function_start + 1:
                if function_lines > 20:
                    issues.append({
                        "id": f"CC{issue_id:03d}",
                        "category": "functions",
                        "severity": "high",
                        "line_number": function_start,
                        "code_snippet": f"Function spans {function_lines} lines",
                        "issue_title": "Function too long",
                        "description": f"Function has {function_lines} lines, exceeding the 20-line guideline",
                        "clean_code_principle": "Small Functions (Chapter 3)",
                        "recommendation": "Break down into smaller, focused functions",
                        "example_fix": "Extract logical groups into separate functions",
                        "impact": "Large functions are harder to understand, test, and maintain",
                        "effort_to_fix": "medium"
                    })
                    issue_id += 1
                in_function = False
                function_lines = 0
        
        # Check for obvious comments that explain what code does
        for i, line in enumerate(lines, 1):
            if '#' in line and any(word in line.lower() for word in ['return', 'add', 'calculate', 'get', 'set']):
                issues.append({
                    "id": f"CC{issue_id:03d}",
                    "category": "comments",
                    "severity": "low",
                    "line_number": i,
                    "code_snippet": line.strip(),
                    "issue_title": "Redundant comment",
                    "description": "Comment explains what the code does instead of why",
                    "clean_code_principle": "Don't Comment Bad Code—Rewrite It (Chapter 4)",
                    "recommendation": "Remove obvious comments or rewrite code to be self-documenting",
                    "example_fix": "Use descriptive function/variable names instead",
                    "impact": "Clutters code without adding value",
                    "effort_to_fix": "low"
                })
                issue_id += 1
        
        # Generate summary
        total_issues = len(issues)
        severity_counts = {
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"])
        }
        category_counts = {}
        for issue in issues:
            cat = issue["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "analysis_summary": {
                "total_issues": total_issues,
                "high_priority": severity_counts["high"],
                "medium_priority": severity_counts["medium"],
                "low_priority": severity_counts["low"],
                "categories": category_counts
            },
            "issues": issues,
            "quick_wins": [issue["recommendation"] for issue in issues if issue["effort_to_fix"] == "low"],
            "deep_analysis_needed": [
                {
                    "issue_id": issue["id"],
                    "reason": "Requires architectural guidance",
                    "suggested_rag_topics": ["function design", "naming conventions"]
                }
                for issue in issues if issue["severity"] == "high"
            ]
        }
    
    async def _simulate_level_1_analysis(self, code: str, language: str, level_0_results: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Level 1 RAG analysis (replace with actual RAG implementation)"""
        await asyncio.sleep(1.0)  # Simulate RAG retrieval time
        
        detailed_issues = []
        book_sections = []
        
        for issue in level_0_results["issues"]:
            # Simulate RAG retrieval and analysis
            if issue["category"] == "naming":
                citation = {
                    "chapter": "Chapter 2: Meaningful Names",
                    "section": "Use Intention-Revealing Names",
                    "page_range": "18-20",
                    "key_quote": "The name of a variable, function, or class, should answer all the big questions. It should tell you why it exists, what it does, and how it is used.",
                    "relevance": "Directly addresses the naming violation identified"
                }
                book_sections.append("Chapter 2: Meaningful Names")
                
            elif issue["category"] == "functions":
                citation = {
                    "chapter": "Chapter 3: Functions",
                    "section": "Small!",
                    "page_range": "34-35",
                    "key_quote": "The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that.",
                    "relevance": "Establishes the principle that functions should be kept short"
                }
                book_sections.append("Chapter 3: Functions")
                
            elif issue["category"] == "comments":
                citation = {
                    "chapter": "Chapter 4: Comments",
                    "section": "Comments Do Not Make Up for Bad Code",
                    "page_range": "55-56",
                    "key_quote": "Don't comment bad code—rewrite it.",
                    "relevance": "Explains why obvious comments should be eliminated"
                }
                book_sections.append("Chapter 4: Comments")
            
            else:
                citation = {
                    "chapter": "Chapter 5: Formatting",
                    "section": "Vertical Formatting",
                    "page_range": "78-80",
                    "key_quote": "We would like a source file to be like a newspaper article.",
                    "relevance": "Provides guidance on code organization"
                }
                book_sections.append("Chapter 5: Formatting")
            
            detailed_issues.append({
                "level_0_issue_id": issue["id"],
                "deep_analysis": {
                    "book_citations": [citation],
                    "comprehensive_explanation": f"This issue relates to fundamental Clean Code principles. {citation['key_quote']} This means that {issue['description'].lower()} represents a violation of core software craftsmanship practices.",
                    "historical_context": "Robert Martin developed this principle based on decades of experience maintaining large codebases.",
                    "common_violations": f"Teams commonly struggle with {issue['category']} because they prioritize speed over clarity.",
                    "refactoring_strategy": f"1. Identify the core responsibility, 2. {issue['recommendation']}, 3. Verify readability improves",
                    "examples_from_book": [
                        {
                            "example_type": "principle_illustration",
                            "description": f"Martin demonstrates this principle throughout {citation['chapter']}",
                            "code_reference": f"Multiple examples in {citation['section']}"
                        }
                    ],
                    "related_principles": ["Single Responsibility Principle", "Code Readability"],
                    "team_discussion_points": [
                        f"How does this {issue['category']} issue affect our team's code review process?",
                        "What coding standards should we establish to prevent this?"
                    ]
                },
                "enhanced_recommendation": {
                    "immediate_action": issue["recommendation"],
                    "long_term_strategy": f"Establish team conventions for {issue['category']} to prevent future occurrences",
                    "code_example": issue["example_fix"],
                    "verification_checklist": [f"Verify {issue['category']} improvement enhances readability"],
                    "learning_resources": [f"{citation['chapter']}, {citation['section']}"]
                }
            })
        
        return {
            "deep_analysis": {
                "total_issues_analyzed": len(detailed_issues),
                "book_sections_referenced": list(set(book_sections)),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "detailed_issues": detailed_issues,
            "synthesis": {
                "overall_code_health": "Needs improvement in naming and structure",
                "primary_focus_areas": ["Meaningful Names", "Function Size", "Comment Quality"],
                "refactoring_roadmap": [
                    {
                        "phase": "Phase 1: Quick Wins",
                        "actions": ["Rename variables", "Remove obvious comments"],
                        "expected_outcome": "Immediate readability improvement"
                    },
                    {
                        "phase": "Phase 2: Structural",
                        "actions": ["Break down large functions", "Improve abstractions"],
                        "expected_outcome": "Better maintainability"
                    }
                ],
                "book_study_recommendations": [
                    {
                        "chapter": "Chapter 2",
                        "sections": ["Use Intention-Revealing Names"],
                        "reason": "Addresses primary naming issues",
                        "study_priority": "high"
                    }
                ]
            }
        }
    
    def generate_final_report(self, level_0_results: Dict[str, Any], level_1_results: Dict[str, Any], 
                             code: str, language: str, filename: str = None) -> str:
        """Generate final Markdown report combining both analysis levels"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_info = f"**File:** `{filename}`\n" if filename else "**Code Snippet Analysis**\n"
        
        report = f"""# Clean Code Analysis Report
        
{file_info}**Language:** {language}  
**Analysis Date:** {timestamp}  
**Pipeline:** Two-Pass Clean Code Review

## 📊 Executive Summary

- **Total Issues Found:** {level_0_results['analysis_summary']['total_issues']}
- **High Priority:** {level_0_results['analysis_summary']['high_priority']}
- **Medium Priority:** {level_0_results['analysis_summary']['medium_priority']}
- **Low Priority:** {level_0_results['analysis_summary']['low_priority']}

### Issue Categories
"""
        
        for category, count in level_0_results['analysis_summary']['categories'].items():
            report += f"- **{category.title()}:** {count} issues\n"
        
        report += "\n## 🚀 Quick Feedback (Level 0 Analysis)\n\n"
        
        if level_0_results['analysis_summary']['total_issues'] == 0:
            report += "✅ **Excellent!** No Clean Code violations detected.\n"
        else:
            for issue in level_0_results['issues']:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[issue['severity']]
                report += f"""### {severity_icon} {issue['issue_title']} (Line {issue['line_number']})

**Principle:** {issue['clean_code_principle']}  
**Impact:** {issue['impact']}  
**Effort:** {issue['effort_to_fix']}

```{language}
{issue['code_snippet']}
```

**Recommendation:** {issue['recommendation']}

**Example Fix:**
```{language}
{issue['example_fix']}
```

---

"""
        
        report += "\n## 📚 Deep Feedback with Citations (Level 1 Analysis)\n\n"
        
        if 'message' in level_1_results:
            report += level_1_results['message']
        else:
            report += f"**Book Sections Referenced:** {', '.join(level_1_results['deep_analysis']['book_sections_referenced'])}\n\n"
            
            for analysis in level_1_results['detailed_issues']:
                issue_id = analysis['level_0_issue_id']
                deep = analysis['deep_analysis']
                enhanced = analysis['enhanced_recommendation']
                
                report += f"""### 📖 Deep Analysis: {issue_id}

#### Book Citations
"""
                for citation in deep['book_citations']:
                    report += f"""
**{citation['chapter']}** - *{citation['section']}* (Pages {citation['page_range']})

> {citation['key_quote']}

*Relevance:* {citation['relevance']}
"""
                
                report += f"""
#### Comprehensive Explanation
{deep['comprehensive_explanation']}

#### Historical Context
{deep['historical_context']}

#### Refactoring Strategy
{deep['refactoring_strategy']}

#### Team Discussion Points
"""
                for point in deep['team_discussion_points']:
                    report += f"- {point}\n"
                
                report += f"""
#### Learning Resources
"""
                for resource in enhanced['learning_resources']:
                    report += f"- {resource}\n"
                
                report += "\n---\n\n"
            
            # Add synthesis section
            synthesis = level_1_results['synthesis']
            report += f"""## 🎯 Synthesis & Roadmap

### Overall Code Health
{synthesis['overall_code_health']}

### Primary Focus Areas
"""
            for area in synthesis['primary_focus_areas']:
                report += f"- {area}\n"
            
            report += "\n### Refactoring Roadmap\n"
            for phase in synthesis['refactoring_roadmap']:
                report += f"""
#### {phase['phase']}
**Actions:** {', '.join(phase['actions'])}  
**Expected Outcome:** {phase['expected_outcome']}
"""
            
            report += "\n### Recommended Study\n"
            for rec in synthesis['book_study_recommendations']:
                report += f"""
**{rec['chapter']}** - {', '.join(rec['sections'])}  
*Priority:* {rec['study_priority']} | *Reason:* {rec['reason']}
"""
        
        report += f"""

## 🎓 Clean Code Principles Applied

This analysis is based on Robert Martin's "Clean Code: A Handbook of Agile Software Craftsmanship."

### Key Principles Used:
- **Chapter 2:** Meaningful Names
- **Chapter 3:** Functions  
- **Chapter 4:** Comments
- **Chapter 5:** Formatting

---

*Generated by SuperClaude Clean Code Two-Pass Analysis Pipeline*
"""
        
        return report
    
    async def analyze_code(self, code: str, filename: str = None) -> Dict[str, Any]:
        """Run complete two-pass analysis pipeline"""
        language = self.detect_language(code, filename)
        
        print(f"🎯 Starting Clean Code Two-Pass Analysis")
        print(f"Language: {language}")
        print(f"Code length: {len(code)} characters")
        print("=" * 50)
        
        # Level 0: Quick analysis
        level_0_results = await self.run_level_0_analysis(code, language)
        
        # Level 1: Deep analysis (only if issues found)
        level_1_results = await self.run_level_1_analysis(code, language, level_0_results)
        
        # Generate final report
        final_report = self.generate_final_report(level_0_results, level_1_results, code, language, filename)
        
        return {
            "level_0_results": level_0_results,
            "level_1_results": level_1_results,
            "final_report": final_report,
            "metadata": {
                "language": language,
                "filename": filename,
                "analysis_timestamp": datetime.now().isoformat(),
                "pipeline_version": "1.0.0"
            }
        }

async def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Clean Code Two-Pass Analysis Pipeline")
    parser.add_argument("--file", help="Path to code file to analyze")
    parser.add_argument("--code", help="Code string to analyze directly")
    parser.add_argument("--output", help="Output file for report (optional)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    if not args.file and not args.code:
        parser.error("Must provide either --file or --code")
    
    # Get code content
    if args.file:
        try:
            with open(args.file, 'r') as f:
                code = f.read()
            filename = args.file
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.file}")
            return 1
    else:
        code = args.code
        filename = None
    
    # Run analysis
    try:
        pipeline = CleanCodePipeline()
        results = await pipeline.analyze_code(code, filename)
        
        if args.format == "json":
            output = json.dumps(results, indent=2)
        else:
            output = results["final_report"]
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"📄 Report saved to: {args.output}")
        else:
            print("\n" + "="*50)
            print("ANALYSIS RESULTS")
            print("="*50)
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))