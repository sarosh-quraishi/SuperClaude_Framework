#!/usr/bin/env python3
"""
Claude API Integration for SuperClaude Multi-Agent Code Review System
Production-ready Claude API integration for real code analysis
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import time

from ..agents import CodeSuggestion, SeverityLevel


@dataclass
class APIConfig:
    """Configuration for Claude API integration"""
    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 50  # Requests per minute
    base_url: str = "https://api.anthropic.com"


@dataclass
class APIMetrics:
    """Track API usage metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None


class RateLimiter:
    """Simple rate limiter for API requests"""
    
    def __init__(self, max_requests_per_minute: int = 50):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limits"""
        now = datetime.now()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(minutes=1)]
        
        # If at limit, wait until we can make another request
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request).seconds
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)


class ClaudeAPIIntegration:
    """Production-ready Claude API integration for code analysis"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.metrics = APIMetrics()
        self.rate_limiter = RateLimiter(config.rate_limit_rpm)
        self.logger = logging.getLogger(__name__)
        
        # Validate API key
        if not config.api_key or config.api_key == "your_api_key_here":
            raise ValueError("Valid Claude API key required. Set ANTHROPIC_API_KEY environment variable.")
    
    async def analyze_with_claude(self, agent_prompt: str, code: str, language: str, 
                                 agent_name: str = "Code Review Agent") -> List[CodeSuggestion]:
        """Perform real analysis using Claude API"""
        
        start_time = time.time()
        
        try:
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Build comprehensive prompt
            full_prompt = self._build_analysis_prompt(agent_prompt, code, language, agent_name)
            
            # Make API request
            response_data = await self._make_api_request(full_prompt)
            
            # Parse and validate response
            suggestions = self._parse_claude_response(response_data, agent_name)
            
            # Update metrics
            self._update_metrics(time.time() - start_time, success=True, 
                               tokens_used=response_data.get('usage', {}).get('output_tokens', 0))
            
            self.logger.info(f"Successfully analyzed code with {agent_name}: {len(suggestions)} suggestions")
            return suggestions
            
        except Exception as e:
            self._update_metrics(time.time() - start_time, success=False)
            self.logger.error(f"Claude API analysis failed for {agent_name}: {e}")
            
            # Return fallback suggestions
            return self._create_fallback_suggestions(agent_name, str(e))
    
    def _build_analysis_prompt(self, agent_prompt: str, code: str, language: str, agent_name: str) -> str:
        """Build comprehensive prompt with context and constraints"""
        
        return f"""You are {agent_name}, an expert code reviewer. Your task is to analyze the provided {language} code and provide structured suggestions for improvement.

{agent_prompt}

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a valid JSON array of suggestions
2. Each suggestion must follow the exact schema provided below
3. Focus on genuinely actionable improvements that provide educational value
4. Consider real-world impact vs theoretical perfection
5. Prioritize suggestions that teach developers WHY changes matter
6. Be specific about line numbers and code snippets when possible

REQUIRED JSON SCHEMA:
[
  {{
    "principle": "Name of the principle/rule being applied (e.g., 'Meaningful Names', 'SQL Injection Prevention')",
    "line_number": 15,
    "original_code": "exact code that needs changing (optional if general advice)",
    "suggested_code": "improved version of the code (optional if general advice)",
    "reasoning": "Brief explanation of why this violates the principle",
    "educational_explanation": "Detailed teaching explanation helping developers understand the underlying concept and when to apply it",
    "impact_score": 7.5,
    "confidence": 0.9,
    "category": "naming|structure|security|performance|testing|design|other"
  }}
]

SCORING GUIDELINES:
- impact_score: 1-10 (10 = critical issue that must be fixed, 1 = minor style suggestion)
- confidence: 0-1 (1 = completely certain this is an issue, 0.5 = uncertain, depends on context)

CODE TO ANALYZE:
```{language}
{code}
```

Remember: Respond ONLY with the JSON array. No additional text, explanations, or markdown formatting."""
    
    async def _make_api_request(self, prompt: str) -> Dict[str, Any]:
        """Make HTTP request to Claude API"""
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
            for attempt in range(self.config.max_retries):
                try:
                    async with session.post(
                        f"{self.config.base_url}/v1/messages",
                        headers=headers,
                        json=payload
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:
                            # Rate limited, wait and retry
                            wait_time = 2 ** attempt
                            self.logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                            await asyncio.sleep(wait_time)
                        else:
                            error_text = await response.text()
                            raise Exception(f"API request failed with status {response.status}: {error_text}")
                            
                except asyncio.TimeoutError:
                    if attempt == self.config.max_retries - 1:
                        raise Exception("API request timed out after all retries")
                    await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    if attempt == self.config.max_retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)
        
        raise Exception("Failed to complete API request after all retries")
    
    def _parse_claude_response(self, response_data: Dict[str, Any], agent_name: str) -> List[CodeSuggestion]:
        """Parse Claude's JSON response into CodeSuggestion objects"""
        
        try:
            content = response_data.get('content', [])
            if not content:
                return []
            
            # Extract text content
            text_content = content[0].get('text', '') if content else ''
            
            # Clean up the response (remove any markdown formatting)
            text_content = text_content.strip()
            if text_content.startswith('```json'):
                text_content = text_content[7:]
            if text_content.endswith('```'):
                text_content = text_content[:-3]
            text_content = text_content.strip()
            
            # Parse JSON
            suggestions_data = json.loads(text_content)
            
            if not isinstance(suggestions_data, list):
                self.logger.warning(f"Expected list of suggestions, got {type(suggestions_data)}")
                return []
            
            suggestions = []
            for suggestion_data in suggestions_data:
                suggestion = self._validate_and_create_suggestion(suggestion_data, agent_name)
                if suggestion:
                    suggestions.append(suggestion)
            
            return suggestions
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response content: {response_data}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing Claude response: {e}")
            return []
    
    def _validate_and_create_suggestion(self, data: Dict[str, Any], agent_name: str) -> Optional[CodeSuggestion]:
        """Validate suggestion data and create CodeSuggestion object"""
        
        try:
            # Validate required fields
            required_fields = ['principle', 'reasoning', 'educational_explanation', 'impact_score', 'confidence']
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Missing required field '{field}' in suggestion")
                    return None
            
            # Validate and normalize data types
            impact_score = float(data['impact_score'])
            confidence = float(data['confidence'])
            
            # Clamp values to valid ranges
            impact_score = max(1.0, min(10.0, impact_score))
            confidence = max(0.0, min(1.0, confidence))
            
            # Determine severity from impact score
            if impact_score >= 9.0:
                severity = SeverityLevel.CRITICAL
            elif impact_score >= 7.0:
                severity = SeverityLevel.HIGH
            elif impact_score >= 5.0:
                severity = SeverityLevel.MEDIUM
            elif impact_score >= 3.0:
                severity = SeverityLevel.LOW
            else:
                severity = SeverityLevel.INFO
            
            # Create suggestion
            return CodeSuggestion(
                id=f"{agent_name}_{int(time.time())}_{hash(data['principle']) % 10000}",
                agent_name=agent_name,
                principle=str(data['principle']),
                line_number=data.get('line_number'),
                original_code=data.get('original_code'),
                suggested_code=data.get('suggested_code'),
                reasoning=str(data['reasoning']),
                educational_explanation=str(data['educational_explanation']),
                impact_score=impact_score,
                confidence=confidence,
                severity=severity,
                category=data.get('category', 'general')
            )
            
        except (ValueError, TypeError, KeyError) as e:
            self.logger.warning(f"Invalid suggestion data: {e}")
            return None
    
    def _create_fallback_suggestions(self, agent_name: str, error_message: str) -> List[CodeSuggestion]:
        """Create fallback suggestions when API fails"""
        
        return [
            CodeSuggestion(
                id=f"{agent_name}_fallback_{int(time.time())}",
                agent_name=agent_name,
                principle="API Service Unavailable",
                line_number=None,
                original_code=None,
                suggested_code=None,
                reasoning=f"Claude API analysis temporarily unavailable: {error_message}",
                educational_explanation="The AI-powered code analysis service is currently unavailable. Please try again later or check your API configuration.",
                impact_score=1.0,
                confidence=1.0,
                severity=SeverityLevel.INFO,
                category="system"
            )
        ]
    
    def _update_metrics(self, response_time: float, success: bool, tokens_used: int = 0):
        """Update API usage metrics"""
        
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.now()
        
        if success:
            self.metrics.successful_requests += 1
            self.metrics.total_tokens_used += tokens_used
            
            # Update average response time
            if self.metrics.successful_requests == 1:
                self.metrics.average_response_time = response_time
            else:
                # Running average
                weight = 1.0 / self.metrics.successful_requests
                self.metrics.average_response_time = (
                    (1 - weight) * self.metrics.average_response_time + 
                    weight * response_time
                )
        else:
            self.metrics.failed_requests += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of API usage metrics"""
        
        success_rate = 0.0
        if self.metrics.total_requests > 0:
            success_rate = self.metrics.successful_requests / self.metrics.total_requests
        
        return {
            "total_requests": self.metrics.total_requests,
            "success_rate": f"{success_rate:.1%}",
            "total_tokens_used": self.metrics.total_tokens_used,
            "average_response_time": f"{self.metrics.average_response_time:.2f}s",
            "last_request": self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None
        }


def create_api_config_from_env() -> APIConfig:
    """Create API configuration from environment variables"""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    return APIConfig(
        api_key=api_key,
        model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
        max_tokens=int(os.getenv('CLAUDE_MAX_TOKENS', '4000')),
        temperature=float(os.getenv('CLAUDE_TEMPERATURE', '0.1')),
        timeout=int(os.getenv('CLAUDE_TIMEOUT', '30')),
        max_retries=int(os.getenv('CLAUDE_MAX_RETRIES', '3')),
        rate_limit_rpm=int(os.getenv('CLAUDE_RATE_LIMIT_RPM', '50'))
    )


async def test_api_integration():
    """Test the Claude API integration"""
    
    try:
        config = create_api_config_from_env()
        api = ClaudeAPIIntegration(config)
        
        test_code = """
def process_user_input(user_data):
    temp = user_data
    if temp:
        print(temp)
    return temp
"""
        
        test_prompt = """You are a Clean Code expert. Analyze this code for naming issues, 
                        function complexity, and adherence to Clean Code principles."""
        
        suggestions = await api.analyze_with_claude(test_prompt, test_code, "python", "Clean Code Agent")
        
        print(f"API Test Results:")
        print(f"Generated {len(suggestions)} suggestions")
        for suggestion in suggestions:
            print(f"- {suggestion.principle}: {suggestion.reasoning}")
        
        print(f"\nAPI Metrics: {api.get_metrics_summary()}")
        
    except Exception as e:
        print(f"API test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_api_integration())