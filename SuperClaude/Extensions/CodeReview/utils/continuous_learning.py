#!/usr/bin/env python3
"""
Continuous Learning Engine for SuperClaude Multi-Agent Code Review System
Learn from user feedback to improve suggestion quality and effectiveness
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from ..agents import CodeSuggestion, SeverityLevel


@dataclass
class SuggestionFeedback:
    """Individual feedback record for a suggestion"""
    suggestion_id: str
    agent_name: str
    principle: str
    user_action: str  # 'accepted', 'rejected', 'modified', 'ignored'
    user_rating: Optional[float] = None  # 1-5 scale
    modification_applied: Optional[str] = None
    time_to_decision: Optional[float] = None  # seconds
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for an individual agent"""
    agent_name: str
    total_suggestions: int = 0
    accepted_suggestions: int = 0
    rejected_suggestions: int = 0
    modified_suggestions: int = 0
    avg_user_rating: float = 0.0
    avg_impact_accuracy: float = 0.0  # How accurate impact scores are
    improvement_trend: float = 0.0  # Positive = improving, negative = declining
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate"""
        total = max(1, self.total_suggestions)
        return (self.accepted_suggestions + self.modified_suggestions) / total
    
    @property
    def pure_acceptance_rate(self) -> float:
        """Calculate pure acceptance rate (no modifications)"""
        return self.accepted_suggestions / max(1, self.total_suggestions)


@dataclass
class PrincipleEffectiveness:
    """Track effectiveness of specific principles/rules"""
    principle: str
    agent_name: str
    total_applications: int = 0
    successful_applications: int = 0
    avg_user_rating: float = 0.0
    common_rejection_reasons: List[str] = field(default_factory=list)
    language_effectiveness: Dict[str, float] = field(default_factory=dict)
    complexity_effectiveness: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class ContinuousLearningEngine:
    """Learn from user feedback to improve suggestions over time"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.expanduser("~/.superclaude/learning")
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Learning data
        self.feedback_history: List[SuggestionFeedback] = []
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.principle_effectiveness: Dict[str, PrincipleEffectiveness] = {}
        self.pattern_insights: Dict[str, Any] = {}
        
        # Load existing data
        self._load_learning_data()
    
    def record_feedback(self, suggestion: CodeSuggestion, user_action: str, 
                       user_rating: Optional[float] = None, 
                       modification_applied: Optional[str] = None,
                       time_to_decision: Optional[float] = None,
                       context: Optional[Dict[str, Any]] = None) -> None:
        """Record user feedback on a suggestion"""
        
        feedback = SuggestionFeedback(
            suggestion_id=suggestion.id,
            agent_name=suggestion.agent_name,
            principle=suggestion.principle,
            user_action=user_action,
            user_rating=user_rating,
            modification_applied=modification_applied,
            time_to_decision=time_to_decision,
            context=context or {}
        )
        
        self.feedback_history.append(feedback)
        
        # Update metrics
        self._update_agent_metrics(feedback, suggestion)
        self._update_principle_effectiveness(feedback, suggestion)
        self._analyze_patterns()
        
        # Persist data
        self._save_learning_data()
        
        self.logger.info(f"Recorded feedback for {suggestion.agent_name}: "
                        f"{user_action} (rating: {user_rating})")
    
    def get_agent_performance(self, agent_name: str) -> Optional[AgentPerformanceMetrics]:
        """Get performance metrics for an agent"""
        return self.agent_metrics.get(agent_name)
    
    def get_principle_effectiveness(self, principle: str, agent_name: str) -> Optional[PrincipleEffectiveness]:
        """Get effectiveness data for a specific principle"""
        key = f"{agent_name}:{principle}"
        return self.principle_effectiveness.get(key)
    
    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get suggestions for system improvements based on learning"""
        suggestions = []
        
        # Agent performance insights
        for agent_name, metrics in self.agent_metrics.items():
            if metrics.acceptance_rate < 0.5 and metrics.total_suggestions > 10:
                suggestions.append({
                    "type": "agent_performance",
                    "agent": agent_name,
                    "issue": "Low acceptance rate",
                    "details": f"Only {metrics.acceptance_rate:.1%} of suggestions accepted",
                    "recommendation": "Review agent prompts and focus areas"
                })
            
            if metrics.improvement_trend < -0.1:
                suggestions.append({
                    "type": "agent_trend",
                    "agent": agent_name,
                    "issue": "Declining performance",
                    "details": f"Performance trend: {metrics.improvement_trend:.2f}",
                    "recommendation": "Agent may need retraining or prompt updates"
                })
        
        # Principle effectiveness insights
        for key, effectiveness in self.principle_effectiveness.items():
            if effectiveness.successful_applications / max(1, effectiveness.total_applications) < 0.3:
                suggestions.append({
                    "type": "principle_effectiveness",
                    "principle": effectiveness.principle,
                    "agent": effectiveness.agent_name,
                    "issue": "Low success rate",
                    "details": f"Only {effectiveness.successful_applications}/{effectiveness.total_applications} successful",
                    "recommendation": "Consider refining this principle or its application criteria"
                })
        
        return suggestions
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get comprehensive learning insights"""
        total_feedback = len(self.feedback_history)
        
        if total_feedback == 0:
            return {"status": "insufficient_data", "message": "No feedback data available"}
        
        # Calculate overall metrics
        recent_feedback = [f for f in self.feedback_history 
                          if (datetime.now() - f.timestamp).days <= 30]
        
        overall_acceptance = len([f for f in recent_feedback 
                                if f.user_action in ['accepted', 'modified']]) / max(1, len(recent_feedback))
        
        avg_rating = np.mean([f.user_rating for f in recent_feedback 
                             if f.user_rating is not None]) if recent_feedback else 0.0
        
        # Agent rankings
        agent_rankings = []
        for agent_name, metrics in self.agent_metrics.items():
            agent_rankings.append({
                "agent": agent_name,
                "acceptance_rate": metrics.acceptance_rate,
                "avg_rating": metrics.avg_user_rating,
                "total_suggestions": metrics.total_suggestions
            })
        agent_rankings.sort(key=lambda x: x["acceptance_rate"], reverse=True)
        
        return {
            "status": "active",
            "total_feedback_records": total_feedback,
            "recent_feedback_count": len(recent_feedback),
            "overall_acceptance_rate": overall_acceptance,
            "average_user_rating": avg_rating,
            "agent_rankings": agent_rankings,
            "improvement_suggestions": self.get_improvement_suggestions(),
            "learning_trends": self._analyze_learning_trends(),
            "pattern_insights": self.pattern_insights
        }
    
    def _update_agent_metrics(self, feedback: SuggestionFeedback, suggestion: CodeSuggestion):
        """Update agent performance metrics"""
        agent_name = feedback.agent_name
        
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentPerformanceMetrics(agent_name=agent_name)
        
        metrics = self.agent_metrics[agent_name]
        metrics.total_suggestions += 1
        metrics.last_updated = datetime.now()
        
        # Update action counts
        if feedback.user_action == 'accepted':
            metrics.accepted_suggestions += 1
        elif feedback.user_action == 'rejected':
            metrics.rejected_suggestions += 1
        elif feedback.user_action == 'modified':
            metrics.modified_suggestions += 1
        
        # Update average user rating
        if feedback.user_rating is not None:
            if metrics.total_suggestions == 1:
                metrics.avg_user_rating = feedback.user_rating
            else:
                # Rolling average
                weight = 1.0 / metrics.total_suggestions
                metrics.avg_user_rating = (
                    (1 - weight) * metrics.avg_user_rating + 
                    weight * feedback.user_rating
                )
        
        # Update impact accuracy (how well the agent predicts impact)
        if feedback.user_rating is not None:
            predicted_impact = suggestion.impact_score / 10.0  # Normalize to 0-1
            actual_impact = feedback.user_rating / 5.0  # Normalize to 0-1
            accuracy = 1.0 - abs(predicted_impact - actual_impact)
            
            if metrics.total_suggestions == 1:
                metrics.avg_impact_accuracy = accuracy
            else:
                weight = 1.0 / metrics.total_suggestions
                metrics.avg_impact_accuracy = (
                    (1 - weight) * metrics.avg_impact_accuracy + 
                    weight * accuracy
                )
    
    def _update_principle_effectiveness(self, feedback: SuggestionFeedback, suggestion: CodeSuggestion):
        """Update principle effectiveness tracking"""
        key = f"{feedback.agent_name}:{feedback.principle}"
        
        if key not in self.principle_effectiveness:
            self.principle_effectiveness[key] = PrincipleEffectiveness(
                principle=feedback.principle,
                agent_name=feedback.agent_name
            )
        
        effectiveness = self.principle_effectiveness[key]
        effectiveness.total_applications += 1
        effectiveness.last_updated = datetime.now()
        
        # Track success
        if feedback.user_action in ['accepted', 'modified']:
            effectiveness.successful_applications += 1
        
        # Update average rating
        if feedback.user_rating is not None:
            if effectiveness.total_applications == 1:
                effectiveness.avg_user_rating = feedback.user_rating
            else:
                weight = 1.0 / effectiveness.total_applications
                effectiveness.avg_user_rating = (
                    (1 - weight) * effectiveness.avg_user_rating + 
                    weight * feedback.user_rating
                )
        
        # Track language-specific effectiveness
        language = feedback.context.get('language', 'unknown')
        if language not in effectiveness.language_effectiveness:
            effectiveness.language_effectiveness[language] = 0.0
        
        success_rate = effectiveness.successful_applications / effectiveness.total_applications
        effectiveness.language_effectiveness[language] = success_rate
    
    def _analyze_patterns(self):
        """Analyze patterns in feedback data"""
        if len(self.feedback_history) < 10:
            return
        
        recent_feedback = self.feedback_history[-100:]  # Last 100 feedback items
        
        # Pattern 1: Time-based acceptance patterns
        time_patterns = defaultdict(list)
        for feedback in recent_feedback:
            hour = feedback.timestamp.hour
            accepted = feedback.user_action in ['accepted', 'modified']
            time_patterns[hour].append(accepted)
        
        # Pattern 2: Language-specific patterns
        language_patterns = defaultdict(lambda: {'total': 0, 'accepted': 0})
        for feedback in recent_feedback:
            language = feedback.context.get('language', 'unknown')
            language_patterns[language]['total'] += 1
            if feedback.user_action in ['accepted', 'modified']:
                language_patterns[language]['accepted'] += 1
        
        # Pattern 3: Decision time patterns
        decision_times = [f.time_to_decision for f in recent_feedback 
                         if f.time_to_decision is not None]
        
        self.pattern_insights = {
            "time_patterns": {
                hour: sum(accepts) / len(accepts) if accepts else 0
                for hour, accepts in time_patterns.items()
            },
            "language_effectiveness": {
                lang: data['accepted'] / max(1, data['total'])
                for lang, data in language_patterns.items()
            },
            "avg_decision_time": np.mean(decision_times) if decision_times else 0,
            "quick_decisions": len([t for t in decision_times if t < 30]) / max(1, len(decision_times))
        }
    
    def _analyze_learning_trends(self) -> Dict[str, Any]:
        """Analyze learning trends over time"""
        if len(self.feedback_history) < 20:
            return {"status": "insufficient_data"}
        
        # Split feedback into time windows
        now = datetime.now()
        windows = {
            "last_week": [f for f in self.feedback_history 
                         if (now - f.timestamp).days <= 7],
            "last_month": [f for f in self.feedback_history 
                          if (now - f.timestamp).days <= 30],
            "older": [f for f in self.feedback_history 
                     if (now - f.timestamp).days > 30]
        }
        
        trends = {}
        for window_name, feedback_list in windows.items():
            if feedback_list:
                acceptance_rate = len([f for f in feedback_list 
                                     if f.user_action in ['accepted', 'modified']]) / len(feedback_list)
                avg_rating = np.mean([f.user_rating for f in feedback_list 
                                    if f.user_rating is not None]) if feedback_list else 0
                trends[window_name] = {
                    "acceptance_rate": acceptance_rate,
                    "avg_rating": avg_rating,
                    "sample_size": len(feedback_list)
                }
        
        return trends
    
    def _load_learning_data(self):
        """Load learning data from disk"""
        try:
            # Load feedback history
            feedback_file = os.path.join(self.data_dir, "feedback_history.json")
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as f:
                    feedback_data = json.load(f)
                
                self.feedback_history = []
                for item in feedback_data:
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.feedback_history.append(SuggestionFeedback(**item))
            
            # Load agent metrics
            metrics_file = os.path.join(self.data_dir, "agent_metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                
                self.agent_metrics = {}
                for agent_name, data in metrics_data.items():
                    data['last_updated'] = datetime.fromisoformat(data['last_updated'])
                    self.agent_metrics[agent_name] = AgentPerformanceMetrics(**data)
            
            # Load principle effectiveness
            principles_file = os.path.join(self.data_dir, "principle_effectiveness.json")
            if os.path.exists(principles_file):
                with open(principles_file, 'r') as f:
                    principles_data = json.load(f)
                
                self.principle_effectiveness = {}
                for key, data in principles_data.items():
                    data['last_updated'] = datetime.fromisoformat(data['last_updated'])
                    self.principle_effectiveness[key] = PrincipleEffectiveness(**data)
            
        except Exception as e:
            self.logger.warning(f"Failed to load learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to disk"""
        try:
            # Save feedback history (keep only last 1000 items)
            feedback_file = os.path.join(self.data_dir, "feedback_history.json")
            feedback_to_save = self.feedback_history[-1000:]  # Keep last 1000
            
            feedback_data = []
            for feedback in feedback_to_save:
                data = asdict(feedback)
                data['timestamp'] = feedback.timestamp.isoformat()
                feedback_data.append(data)
            
            with open(feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=2)
            
            # Save agent metrics
            metrics_file = os.path.join(self.data_dir, "agent_metrics.json")
            metrics_data = {}
            for agent_name, metrics in self.agent_metrics.items():
                data = asdict(metrics)
                data['last_updated'] = metrics.last_updated.isoformat()
                metrics_data[agent_name] = data
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Save principle effectiveness
            principles_file = os.path.join(self.data_dir, "principle_effectiveness.json")
            principles_data = {}
            for key, effectiveness in self.principle_effectiveness.items():
                data = asdict(effectiveness)
                data['last_updated'] = effectiveness.last_updated.isoformat()
                principles_data[key] = data
            
            with open(principles_file, 'w') as f:
                json.dump(principles_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")


def create_learning_engine() -> ContinuousLearningEngine:
    """Create a continuous learning engine instance"""
    return ContinuousLearningEngine()


if __name__ == "__main__":
    # Test the continuous learning engine
    engine = ContinuousLearningEngine()
    
    # Simulate some feedback
    from ..agents import CodeSuggestion, SeverityLevel
    
    test_suggestion = CodeSuggestion(
        id="test_001",
        agent_name="Clean Code Agent",
        principle="Meaningful Names",
        line_number=1,
        original_code="temp = x",
        suggested_code="user_input = x",
        reasoning="Variable name should be descriptive",
        educational_explanation="Use meaningful variable names",
        impact_score=5.0,
        confidence=0.8,
        severity=SeverityLevel.MEDIUM,
        category="naming"
    )
    
    engine.record_feedback(
        suggestion=test_suggestion,
        user_action="accepted",
        user_rating=4.5,
        context={"language": "python"}
    )
    
    insights = engine.get_learning_insights()
    print("Learning Insights:")
    print(json.dumps(insights, indent=2, default=str))