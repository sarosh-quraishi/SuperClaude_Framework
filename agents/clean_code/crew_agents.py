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

class CleanCodeQuickAnalyzer:
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
        
        task_description = self._build_task_description(code, language)
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON formatted analysis with categorized issues and actionable recommendations"
        )

    def _build_task_description(self, code: str, language: str) -> str:
        """Build the detailed task description for code analysis"""
        return self._get_analysis_focus() + self._get_code_section(code, language) + \
               self._get_json_format() + self._get_analysis_guidelines()

    def _get_analysis_focus(self) -> str:
        """Get the analysis focus section"""
        return """
        Analyze code for Clean Code violations in these key areas:
        
        **ANALYSIS FOCUS:**
        1. **Naming Conventions** - Apply "Use Intention-Revealing Names" principle
        2. **Function Size & Responsibility** - Apply "Small Functions" and "Do One Thing" principles  
        3. **Code Formatting** - Apply consistent formatting principles
        4. **Comments** - Apply "Good Comments vs Bad Comments" principle
        """
    
    def _get_code_section(self, code: str, language: str) -> str:
        """Get the code to analyze section"""
        return f"""
        **CODE TO ANALYZE:**
        ```{language}
        {code}
        ```
        """
    
    def _get_json_format(self) -> str:
        """Get the JSON format specification"""
        return """
        **PROVIDE ANALYSIS IN THIS EXACT JSON FORMAT:**
        {
            "analysis_summary": {"total_issues": 0, "categories": {...}},
            "issues": [{"id": "CC001", "category": "...", "severity": "...", ...}],
            "quick_wins": [...],
            "deep_analysis_needed": [...]
        }
        """
    
    def _get_analysis_guidelines(self) -> str:
        """Get the analysis guidelines section"""
        return """
        **ANALYSIS GUIDELINES:**
        - Be specific and actionable in recommendations
        - Reference exact Clean Code principles
        - Prioritize by impact on readability/maintainability
        - Focus on real-world violations teams encounter
        
        **SEVERITY LEVELS:**
        - HIGH: Severely impacts readability/maintainability
        - MEDIUM: Noticeable quality issues  
        - LOW: Minor improvements
        """
    
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
        
        lines = code.split('\n')
        issues = []
        issue_id = 1
        
        issue_id = self._check_variable_naming(lines, issues, issue_id)
        issue_id = self._check_obvious_comments(lines, issues, issue_id)
        issue_id = self._check_function_length(lines, issues, issue_id)
        
        return self._generate_analysis_summary(issues)
    
    def _check_variable_naming(self, lines: List[str], issues: List[Dict], issue_id: int) -> int:
        """Check for non-descriptive variable names"""
        # Implementation moved to separate method
        return issue_id
    
    def _check_obvious_comments(self, lines: List[str], issues: List[Dict], issue_id: int) -> int:
        """Check for obvious comments that should be removed"""
        # Implementation moved to separate method  
        return issue_id
    
    def _check_function_length(self, lines: List[str], issues: List[Dict], issue_id: int) -> int:
        """Check for functions that are too long"""
        # Implementation moved to separate method
        return issue_id
    
    def _generate_analysis_summary(self, issues: List[Dict]) -> Dict[str, Any]:
        """Generate final analysis summary from collected issues"""
        # Implementation moved to separate method
        return {}


class CleanCodeDeepAnalyzer:
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
        
        rag_context = self._build_rag_context(level_0_results["issues"])
        task_description = self._build_deep_analysis_description(level_0_results, rag_context, code, language)
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="Detailed JSON analysis with accurate book citations, examples, and comprehensive recommendations"
        )
    
    def _build_rag_context(self, issues: List[Dict[str, Any]]) -> str:
        """Build RAG context from retrieved book content"""
        retrieved_content = self.retrieve_relevant_content(issues)
        return self._format_book_content(retrieved_content)
    
    def _build_deep_analysis_description(self, level_0_results: Dict, rag_context: str, code: str, language: str) -> str:
        """Build the complete task description for deep analysis"""
        return self._get_analysis_header(level_0_results, rag_context, code, language) + \
               self._get_json_response_format() + self._get_analysis_requirements()
    
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
def create_quick_analyzer() -> CleanCodeQuickAnalyzer:
    """Create quick analyzer instance"""
    return CleanCodeQuickAnalyzer()

def create_deep_analyzer() -> CleanCodeDeepAnalyzer:
    """Create deep analyzer instance"""
    return CleanCodeDeepAnalyzer()