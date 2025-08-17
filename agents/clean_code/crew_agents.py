#!/usr/bin/env python3
"""
Crew AI Agents for Clean Code Analysis

Real Crew AI implementation using Claude for Level 0 and Level 1 agents.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    from langchain_anthropic import ChatAnthropic
    CREW_AVAILABLE = True
except ImportError:
    print("⚠️  CrewAI not installed. Run: pip install -r requirements_clean_code.txt")
    CREW_AVAILABLE = False

from .rag_system import get_clean_code_rag

class CleanCodeLevel0Agent:
    """Level 0 Crew AI Agent for quick Clean Code analysis using Claude"""
    
    def __init__(self):
        if not CREW_AVAILABLE:
            raise ImportError("CrewAI not installed")
        
        # Initialize Claude LLM (using ANTHROPIC_API_KEY environment variable)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=4000
        )
        
        # Create the agent
        self.agent = Agent(
            role="Clean Code Analyst - Quick Review",
            goal="Identify and flag basic Clean Code violations for quick improvement",
            backstory="""You are an expert software engineer specializing in Clean Code practices as defined by Robert Martin (Uncle Bob).
            Your role is to perform rapid, lightweight analysis to identify the most common and impactful code quality issues.
            You focus on immediate, actionable improvements that developers can implement quickly.
            
            You excel at:
            - Identifying naming violations (single letters, abbreviations, unclear intent)
            - Spotting functions that are too long or do too many things
            - Finding unnecessary or misleading comments
            - Detecting formatting inconsistencies
            
            You always provide specific, actionable feedback with concrete examples.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_analysis_task(self, code: str, language: str) -> Task:
        """Create analysis task for the agent"""
        
        task_description = f"""
        Analyze the following {language} code for Clean Code violations in these key areas:

        **ANALYSIS FOCUS:**
        1. **Naming Conventions** - Apply "Use Intention-Revealing Names" principle
           - Are variable/function/class names meaningful and self-documenting?
           - Do names reveal intent without requiring comments?
           - Are abbreviations or single-letter variables used inappropriately?

        2. **Function Size & Responsibility** - Apply "Small Functions" and "Do One Thing" principles
           - Are functions too long (>20 lines guideline)?
           - Does each function do one thing well?
           - Are there obvious extraction opportunities?

        3. **Code Formatting** - Apply consistent formatting principles
           - Is indentation consistent?
           - Are there appropriate blank lines for readability?
           - Is the code properly structured?

        4. **Comments** - Apply "Good Comments vs Bad Comments" principle
           - Are there unnecessary comments explaining obvious code?
           - Are there missing comments for complex business logic?
           - Do comments explain "why" rather than "what"?

        **CODE TO ANALYZE:**
        ```{language}
        {code}
        ```

        **PROVIDE ANALYSIS IN THIS EXACT JSON FORMAT:**
        {{
            "analysis_summary": {{
                "total_issues": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0,
                "categories": {{
                    "naming": 0,
                    "functions": 0,
                    "comments": 0,
                    "formatting": 0
                }}
            }},
            "issues": [
                {{
                    "id": "CC001",
                    "category": "naming|functions|comments|formatting",
                    "severity": "high|medium|low",
                    "line_number": 10,
                    "code_snippet": "problematic code here",
                    "issue_title": "Brief descriptive title",
                    "description": "Clear explanation of what's wrong",
                    "clean_code_principle": "Specific Robert Martin principle violated",
                    "recommendation": "Specific actionable fix",
                    "example_fix": "Show improved code",
                    "impact": "Why this matters for code quality",
                    "effort_to_fix": "low|medium|high"
                }}
            ],
            "quick_wins": [
                "List of easiest fixes that provide immediate value"
            ],
            "deep_analysis_needed": [
                {{
                    "issue_id": "CC001",
                    "reason": "Complex architectural concern needing detailed analysis",
                    "suggested_rag_topics": ["function design", "abstraction levels"]
                }}
            ]
        }}

        **ANALYSIS GUIDELINES:**
        - Be specific and actionable in your recommendations
        - Reference exact Clean Code principles by chapter/concept name
        - Prioritize issues by impact on readability and maintainability
        - Flag complex issues that would benefit from deeper book-based analysis
        - Focus on violations that real development teams encounter daily
        - Suggest concrete improvements with examples, not just identify problems
        - Consider the context and don't flag every single-letter loop variable

        **SEVERITY LEVELS:**
        - HIGH: Severely impacts readability/maintainability (very long functions, completely unclear names)
        - MEDIUM: Noticeable quality issues (somewhat unclear names, minor formatting issues, unnecessary comments)
        - LOW: Minor improvements (optimization opportunities, style preferences)

        Remember: You are Claude, an AI assistant created by Anthropic. Provide thoughtful, practical analysis.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted analysis with categorized issues and actionable recommendations"
        )
    
    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Run Level 0 analysis using CrewAI with Claude"""
        
        task = self.create_analysis_task(code, language)
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Parse the result (assuming it returns JSON)
        try:
            import json
            if isinstance(result, str):
                # Try to extract JSON from the response
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    analysis_result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                analysis_result = result
        except Exception as e:
            print(f"⚠️  JSON parsing failed: {e}, using fallback analysis")
            # Fallback: create structured result
            analysis_result = self._parse_text_result(result, code, language)
        
        return analysis_result
    
    def _parse_text_result(self, result: str, code: str, language: str) -> Dict[str, Any]:
        """Parse text result into structured format if JSON parsing fails"""
        
        # Basic fallback parsing using simple heuristics
        lines = code.split('\n')
        issues = []
        
        issue_id = 1
        
        # Check for short variable names (but exclude common loop variables)
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            # Look for problematic single-letter variables (not in for loops)
            if not line_stripped.startswith('for ') and not line_stripped.startswith('while '):
                short_vars = ['x', 'y', 'a', 'b', 'data', 'result', 'temp', 'val']
                for var in short_vars:
                    if f' {var} ' in line or f' {var}=' in line or f'({var},' in line:
                        issues.append({
                            "id": f"CC{issue_id:03d}",
                            "category": "naming",
                            "severity": "medium",
                            "line_number": i,
                            "code_snippet": line.strip(),
                            "issue_title": "Non-descriptive variable names",
                            "description": f"Variable '{var}' doesn't reveal its intention or purpose",
                            "clean_code_principle": "Use Intention-Revealing Names (Chapter 2)",
                            "recommendation": f"Rename '{var}' to describe what it represents",
                            "example_fix": line.strip().replace(var, f"descriptive_{var}_name"),
                            "impact": "Makes code harder to understand and maintain",
                            "effort_to_fix": "low"
                        })
                        issue_id += 1
                        break
        
        # Check for obvious comments
        for i, line in enumerate(lines, 1):
            if '#' in line:
                comment_part = line[line.index('#'):].strip()
                if any(word in comment_part.lower() for word in ['return', 'add', 'calculate', 'get', 'set']):
                    issues.append({
                        "id": f"CC{issue_id:03d}",
                        "category": "comments",
                        "severity": "low",
                        "line_number": i,
                        "code_snippet": line.strip(),
                        "issue_title": "Obvious comment",
                        "description": "Comment explains what the code does instead of why",
                        "clean_code_principle": "Don't Comment Bad Code—Rewrite It (Chapter 4)",
                        "recommendation": "Remove obvious comments or rewrite code to be self-documenting",
                        "example_fix": "Use descriptive function/variable names instead of comments",
                        "impact": "Clutters code without adding value",
                        "effort_to_fix": "low"
                    })
                    issue_id += 1
        
        # Basic function length check
        in_function = False
        function_lines = 0
        function_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def ') and ':' in line:
                if in_function and function_lines > 25:
                    issues.append({
                        "id": f"CC{issue_id:03d}",
                        "category": "functions",
                        "severity": "high",
                        "line_number": function_start,
                        "code_snippet": f"Function spans {function_lines} lines",
                        "issue_title": "Function too long",
                        "description": f"Function has {function_lines} lines, exceeding Clean Code guidelines",
                        "clean_code_principle": "Small Functions (Chapter 3)",
                        "recommendation": "Break down into smaller, focused functions",
                        "example_fix": "Extract logical groups into separate helper functions",
                        "impact": "Large functions are harder to understand, test, and maintain",
                        "effort_to_fix": "medium"
                    })
                    issue_id += 1
                
                in_function = True
                function_start = i
                function_lines = 1
            elif in_function:
                if line.strip():
                    function_lines += 1
                elif function_lines > 0:  # End of function
                    if function_lines > 25:
                        issues.append({
                            "id": f"CC{issue_id:03d}",
                            "category": "functions", 
                            "severity": "high",
                            "line_number": function_start,
                            "code_snippet": f"Function spans {function_lines} lines",
                            "issue_title": "Function too long",
                            "description": f"Function has {function_lines} lines, exceeding Clean Code guidelines",
                            "clean_code_principle": "Small Functions (Chapter 3)",
                            "recommendation": "Break down into smaller, focused functions",
                            "example_fix": "Extract logical groups into separate helper functions",
                            "impact": "Large functions are harder to understand, test, and maintain",
                            "effort_to_fix": "medium"
                        })
                        issue_id += 1
                    in_function = False
                    function_lines = 0
        
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


class CleanCodeLevel1Agent:
    """Level 1 Crew AI Agent with RAG for deep Clean Code analysis using Claude"""
    
    def __init__(self):
        if not CREW_AVAILABLE:
            raise ImportError("CrewAI not installed")
        
        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=8000
        )
        
        # Initialize RAG system
        self.rag = get_clean_code_rag()
        
        # Create the agent
        self.agent = Agent(
            role="Clean Code Expert with Book Knowledge",
            goal="Provide deep, citation-backed analysis using Clean Code book content",
            backstory="""You are a master software craftsman with deep knowledge of Robert Martin's "Clean Code" book.
            You have access to the entire book content through a retrieval system and can find specific chapters, 
            sections, and examples to provide authoritative guidance. 
            
            Your responses include exact citations and detailed explanations that help developers understand 
            not just what to fix, but why it matters and how to think about code quality systematically.
            
            You excel at:
            - Connecting code issues to specific Clean Code principles
            - Providing exact quotes and citations from the book
            - Explaining the historical context and reasoning behind principles
            - Offering step-by-step refactoring strategies
            - Suggesting learning paths for teams
            
            You are Claude, an AI assistant created by Anthropic, with specialized knowledge of Clean Code practices.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def retrieve_relevant_content(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve relevant book content for each issue"""
        
        content_by_issue = {}
        
        for issue in issues:
            # Create search queries based on issue
            queries = []
            
            if issue["category"] == "naming":
                queries = [
                    "meaningful names intention revealing",
                    "use intention revealing names",
                    "variable function class names",
                    "avoid mental mapping"
                ]
            elif issue["category"] == "functions":
                queries = [
                    "functions small do one thing",
                    "function should be small",
                    "do one thing well",
                    "function arguments parameters"
                ]
            elif issue["category"] == "comments":
                queries = [
                    "comments bad code rewrite",
                    "don't comment bad code",
                    "good comments vs bad comments",
                    "comment quality"
                ]
            elif issue["category"] == "formatting":
                queries = [
                    "formatting vertical horizontal",
                    "code formatting newspaper",
                    "vertical formatting team rules",
                    "indentation consistency"
                ]
            else:
                queries = [issue["description"], issue["clean_code_principle"]]
            
            # Retrieve content for each query
            all_chunks = []
            for query in queries:
                try:
                    chunks = self.rag.retrieve_relevant_chunks(query, n_results=3)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"⚠️  RAG retrieval failed for '{query}': {e}")
            
            # Remove duplicates and keep best matches
            seen_chunks = set()
            unique_chunks = []
            for chunk in all_chunks:
                chunk_key = f"{chunk['metadata']['page_number']}_{chunk['metadata']['chapter']}"
                if chunk_key not in seen_chunks:
                    seen_chunks.add(chunk_key)
                    unique_chunks.append(chunk)
            
            content_by_issue[issue["id"]] = unique_chunks[:5]  # Top 5 unique chunks
        
        return content_by_issue
    
    def create_deep_analysis_task(self, level_0_results: Dict[str, Any], code: str, language: str) -> Task:
        """Create deep analysis task with RAG content"""
        
        # Get relevant content from the book
        retrieved_content = self.retrieve_relevant_content(level_0_results["issues"])
        
        # Build context with book content
        rag_context = ""
        for issue_id, chunks in retrieved_content.items():
            if chunks:
                rag_context += f"\n**Book content for issue {issue_id}:**\n"
                for i, chunk in enumerate(chunks[:3], 1):  # Top 3 chunks per issue
                    rag_context += f"{i}. Chapter: {chunk['metadata']['chapter']}\n"
                    rag_context += f"   Section: {chunk['metadata']['section']}\n"
                    rag_context += f"   Page: {chunk['metadata']['page_number']}\n"
                    rag_context += f"   Content: {chunk['text'][:400]}...\n\n"
        
        task_description = f"""
        You are analyzing code issues that were flagged by the Level 0 Clean Code agent.
        Use the retrieved content from Robert Martin's "Clean Code" book to provide detailed,
        citation-backed analysis and guidance.

        **LEVEL 0 ANALYSIS RESULTS:**
        {level_0_results}

        **RETRIEVED CLEAN CODE BOOK CONTENT:**
        {rag_context}

        **CODE BEING ANALYZED:**
        ```{language}
        {code}
        ```

        **YOUR TASK:**
        For each issue flagged by Level 0, provide deep analysis using the Clean Code book content.
        Use the retrieved book content to provide specific citations, quotes, and detailed guidance.

        **RESPONSE FORMAT (JSON):**
        {{
            "deep_analysis": {{
                "total_issues_analyzed": 0,
                "book_sections_referenced": [],
                "analysis_timestamp": "2024-01-01T12:00:00Z"
            }},
            "detailed_issues": [
                {{
                    "level_0_issue_id": "CC001",
                    "deep_analysis": {{
                        "book_citations": [
                            {{
                                "chapter": "Chapter 3: Functions",
                                "section": "Do One Thing",
                                "page_range": "35-37",
                                "key_quote": "FUNCTIONS SHOULD DO ONE THING. THEY SHOULD DO IT WELL. THEY SHOULD DO IT ONLY.",
                                "relevance": "Directly addresses the multi-responsibility function identified"
                            }}
                        ],
                        "comprehensive_explanation": "Based on the retrieved book content, explain the issue in detail...",
                        "historical_context": "Why Robert Martin developed this principle...",
                        "common_violations": "Typical ways developers violate this principle...",
                        "refactoring_strategy": "Step-by-step approach to fix this specific issue...",
                        "examples_from_book": [
                            {{
                                "example_type": "before_after",
                                "description": "Book example showing transformation",
                                "code_reference": "Reference to specific listings or examples"
                            }}
                        ],
                        "related_principles": ["Single Responsibility", "Abstraction Levels"],
                        "team_discussion_points": [
                            "Specific questions for team to consider during code review"
                        ]
                    }},
                    "enhanced_recommendation": {{
                        "immediate_action": "Specific first step to take",
                        "long_term_strategy": "How to prevent this pattern in the future",
                        "code_example": "Improved version with explanation",
                        "verification_checklist": ["How to verify the fix works"],
                        "learning_resources": ["Specific book sections to study"]
                    }}
                }}
            ],
            "synthesis": {{
                "overall_code_health": "Assessment based on Clean Code standards",
                "primary_focus_areas": ["Top 3 areas needing attention"],
                "refactoring_roadmap": [
                    {{
                        "phase": "Phase 1: Quick Wins",
                        "actions": ["Immediate improvements"],
                        "expected_outcome": "What team will gain"
                    }}
                ],
                "book_study_recommendations": [
                    {{
                        "chapter": "Chapter 3",
                        "sections": ["Do One Thing", "Small Functions"],
                        "reason": "Addresses multiple issues found",
                        "study_priority": "high"
                    }}
                ]
            }}
        }}

        **ANALYSIS REQUIREMENTS:**
        - Use the retrieved book content to provide specific, accurate citations
        - Extract relevant quotes from the retrieved content
        - Reference specific chapters, sections, and pages from the retrieved content
        - Connect issues to broader Clean Code philosophy using book content
        - Provide concrete learning paths based on the book structure
        - Explain historical context when the retrieved content provides it
        - Be accurate - only cite content that was actually retrieved

        Remember: You are Claude, created by Anthropic. Use the retrieved book content to provide 
        authoritative, citation-backed guidance on Clean Code practices.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="Detailed JSON analysis with accurate book citations, examples, and comprehensive recommendations"
        )
    
    async def analyze_code(self, code: str, language: str, level_0_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run Level 1 deep analysis with RAG using Claude"""
        
        if level_0_results['analysis_summary']['total_issues'] == 0:
            return {"message": "No issues requiring deep analysis"}
        
        task = self.create_deep_analysis_task(level_0_results, code, language)
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Parse the result
        try:
            import json
            from datetime import datetime
            
            if isinstance(result, str):
                # Try to extract JSON from the response
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    analysis_result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                analysis_result = result
            
            # Ensure timestamp is set
            if "deep_analysis" in analysis_result:
                analysis_result["deep_analysis"]["analysis_timestamp"] = datetime.now().isoformat()
                
        except Exception as e:
            print(f"⚠️  JSON parsing failed: {e}, using fallback analysis")
            # Fallback: create basic structured result
            analysis_result = self._create_fallback_analysis(level_0_results, code, language)
        
        return analysis_result
    
    def _create_fallback_analysis(self, level_0_results: Dict[str, Any], code: str, language: str) -> Dict[str, Any]:
        """Create fallback analysis if Crew AI fails"""
        from datetime import datetime
        
        detailed_issues = []
        book_sections = []
        
        for issue in level_0_results["issues"]:
            # Try to get real content from RAG if available
            try:
                if issue["category"] == "naming":
                    query = "meaningful names intention revealing"
                elif issue["category"] == "functions":
                    query = "functions small do one thing"
                elif issue["category"] == "comments":
                    query = "comments bad code rewrite"
                else:
                    query = "formatting vertical horizontal"
                
                rag_chunks = self.rag.retrieve_relevant_chunks(query, n_results=1)
                
                if rag_chunks:
                    chunk = rag_chunks[0]
                    chapter_info = {
                        "chapter": chunk['metadata']['chapter'],
                        "section": chunk['metadata']['section'],
                        "page_range": f"{chunk['metadata']['page_number']}",
                        "key_quote": chunk['text'][:200] + "...",
                        "relevance": f"Retrieved content addressing {issue['category']} issues"
                    }
                    book_sections.append(chunk['metadata']['chapter'])
                else:
                    raise Exception("No RAG content available")
                    
            except Exception:
                # Fallback to static mapping
                if issue["category"] == "naming":
                    chapter_info = {
                        "chapter": "Chapter 2: Meaningful Names",
                        "section": "Use Intention-Revealing Names",
                        "page_range": "18-20",
                        "key_quote": "The name of a variable, function, or class, should answer all the big questions.",
                        "relevance": "Directly addresses the naming violation identified"
                    }
                    book_sections.append("Chapter 2: Meaningful Names")
                elif issue["category"] == "functions":
                    chapter_info = {
                        "chapter": "Chapter 3: Functions",
                        "section": "Small!",
                        "page_range": "34-35",
                        "key_quote": "The first rule of functions is that they should be small.",
                        "relevance": "Establishes the principle that functions should be kept short"
                    }
                    book_sections.append("Chapter 3: Functions")
                elif issue["category"] == "comments":
                    chapter_info = {
                        "chapter": "Chapter 4: Comments",
                        "section": "Comments Do Not Make Up for Bad Code",
                        "page_range": "55-56",
                        "key_quote": "Don't comment bad code—rewrite it.",
                        "relevance": "Explains why obvious comments should be eliminated"
                    }
                    book_sections.append("Chapter 4: Comments")
                else:
                    chapter_info = {
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
                    "book_citations": [chapter_info],
                    "comprehensive_explanation": f"According to Clean Code principles, {issue['description']}. {chapter_info['key_quote']} This principle emphasizes the importance of {issue['category']} in maintaining code quality.",
                    "historical_context": "Robert Martin developed these principles based on decades of experience maintaining large codebases across various industries.",
                    "common_violations": f"Teams commonly struggle with {issue['category']} because they prioritize speed over clarity during development cycles.",
                    "refactoring_strategy": f"1. Identify the core issue: {issue['description']}, 2. Apply the fix: {issue['recommendation']}, 3. Verify improvement through code review",
                    "examples_from_book": [{"example_type": "principle_illustration", "description": f"Multiple examples throughout {chapter_info['chapter']}"}],
                    "related_principles": ["Code Readability", "Maintainability", "Software Craftsmanship"],
                    "team_discussion_points": [
                        f"How does this {issue['category']} issue affect our code review process?",
                        f"What team standards should we establish for {issue['category']}?"
                    ]
                },
                "enhanced_recommendation": {
                    "immediate_action": issue["recommendation"],
                    "long_term_strategy": f"Establish team conventions and code review checklists for {issue['category']} quality",
                    "code_example": issue["example_fix"],
                    "verification_checklist": [f"Verify {issue['category']} improvement enhances code readability"],
                    "learning_resources": [f"{chapter_info['chapter']}, {chapter_info['section']}"]
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
                "overall_code_health": "Code shows common quality issues that can be addressed through Clean Code principles",
                "primary_focus_areas": ["Code Readability", "Maintainability", "Team Standards"],
                "refactoring_roadmap": [
                    {
                        "phase": "Phase 1: Quick Wins",
                        "actions": ["Address naming issues", "Remove unnecessary comments", "Fix formatting"],
                        "expected_outcome": "Immediate readability improvement"
                    },
                    {
                        "phase": "Phase 2: Structural",
                        "actions": ["Break down large functions", "Establish team conventions"],
                        "expected_outcome": "Better long-term maintainability"
                    }
                ],
                "book_study_recommendations": [
                    {
                        "chapter": "Chapter 2",
                        "sections": ["Use Intention-Revealing Names"],
                        "reason": "Core naming principles apply to multiple issues",
                        "study_priority": "high"
                    }
                ]
            }
        }


# Factory functions for creating agents
def create_level_0_agent() -> CleanCodeLevel0Agent:
    """Create Level 0 agent instance"""
    return CleanCodeLevel0Agent()

def create_level_1_agent() -> CleanCodeLevel1Agent:
    """Create Level 1 agent instance"""
    return CleanCodeLevel1Agent()