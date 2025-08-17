#!/usr/bin/env python3
"""
Performance Analytics and Metrics Dashboard for SuperClaude Multi-Agent Code Review System
Real-time monitoring, performance analysis, and comprehensive reporting
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import threading
from statistics import mean, median, stdev


@dataclass
class PerformanceMetrics:
    """Core performance metrics"""
    response_time: float
    token_usage: int
    memory_usage: float  # MB
    cpu_usage: float  # Percentage
    suggestions_generated: int
    conflicts_detected: int
    conflicts_resolved: int
    synergies_found: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SystemHealth:
    """System health indicators"""
    api_status: str  # 'healthy', 'degraded', 'down'
    collaboration_engine_status: str
    learning_engine_status: str
    overall_status: str
    error_rate: float
    success_rate: float
    avg_response_time: float
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class QualityMetrics:
    """Code review quality metrics"""
    total_reviews: int = 0
    avg_suggestions_per_review: float = 0.0
    avg_user_rating: float = 0.0
    suggestion_acceptance_rate: float = 0.0
    conflict_resolution_rate: float = 0.0
    educational_value_score: float = 0.0
    code_improvement_score: float = 0.0
    last_calculated: datetime = field(default_factory=datetime.now)


@dataclass
class UsageAnalytics:
    """Usage pattern analytics"""
    daily_reviews: Dict[str, int] = field(default_factory=dict)
    hourly_patterns: Dict[int, float] = field(default_factory=dict)
    language_usage: Dict[str, int] = field(default_factory=dict)
    agent_usage: Dict[str, int] = field(default_factory=dict)
    peak_usage_times: List[str] = field(default_factory=list)
    user_engagement_score: float = 0.0


class MetricsDashboard:
    """Real-time performance analytics and metrics dashboard"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.expanduser("~/.superclaude/metrics")
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Real-time metrics storage
        self.performance_history = deque(maxlen=1000)  # Last 1000 operations
        self.system_health = SystemHealth(
            api_status='unknown',
            collaboration_engine_status='unknown',
            learning_engine_status='unknown',
            overall_status='initializing',
            error_rate=0.0,
            success_rate=0.0,
            avg_response_time=0.0
        )
        
        # Aggregated metrics
        self.quality_metrics = QualityMetrics()
        self.usage_analytics = UsageAnalytics()
        
        # Background monitoring
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self._monitor_thread.start()
        
        # Load historical data
        self._load_metrics_data()
    
    def record_operation(self, operation_type: str, duration: float, 
                        token_usage: int = 0, memory_mb: float = 0.0,
                        success: bool = True, metadata: Optional[Dict] = None):
        """Record a single operation's performance metrics"""
        
        metrics = PerformanceMetrics(
            response_time=duration,
            token_usage=token_usage,
            memory_usage=memory_mb,
            cpu_usage=self._get_cpu_usage(),
            suggestions_generated=metadata.get('suggestions', 0) if metadata else 0,
            conflicts_detected=metadata.get('conflicts', 0) if metadata else 0,
            conflicts_resolved=metadata.get('resolved_conflicts', 0) if metadata else 0,
            synergies_found=metadata.get('synergies', 0) if metadata else 0
        )
        
        self.performance_history.append(metrics)
        
        # Update system health in real-time
        self._update_system_health()
        
        # Update usage analytics
        self._update_usage_analytics(operation_type, metadata)
        
        self.logger.debug(f"Recorded {operation_type} operation: "
                         f"{duration:.3f}s, {token_usage} tokens, success={success}")
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time performance metrics"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        recent_metrics = list(self.performance_history)[-10:]  # Last 10 operations
        
        return {
            "current_performance": {
                "avg_response_time": mean(m.response_time for m in recent_metrics),
                "avg_token_usage": mean(m.token_usage for m in recent_metrics),
                "avg_memory_usage": mean(m.memory_usage for m in recent_metrics),
                "avg_suggestions": mean(m.suggestions_generated for m in recent_metrics),
                "operations_per_minute": self._calculate_ops_per_minute()
            },
            "system_health": asdict(self.system_health),
            "quality_indicators": {
                "avg_conflicts_per_operation": mean(m.conflicts_detected for m in recent_metrics),
                "conflict_resolution_rate": self._calculate_resolution_rate(recent_metrics),
                "synergy_detection_rate": mean(m.synergies_found for m in recent_metrics)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_performance_summary(self, time_window: str = "24h") -> Dict[str, Any]:
        """Get performance summary for specified time window"""
        
        cutoff_time = self._get_cutoff_time(time_window)
        relevant_metrics = [m for m in self.performance_history 
                          if m.timestamp >= cutoff_time]
        
        if not relevant_metrics:
            return {"status": "insufficient_data", "time_window": time_window}
        
        # Performance statistics
        response_times = [m.response_time for m in relevant_metrics]
        token_usage = [m.token_usage for m in relevant_metrics]
        
        performance_stats = {
            "response_time": {
                "mean": mean(response_times),
                "median": median(response_times),
                "p95": self._percentile(response_times, 95),
                "p99": self._percentile(response_times, 99),
                "std_dev": stdev(response_times) if len(response_times) > 1 else 0
            },
            "token_usage": {
                "mean": mean(token_usage),
                "median": median(token_usage),
                "total": sum(token_usage),
                "p95": self._percentile(token_usage, 95)
            },
            "operation_count": len(relevant_metrics),
            "time_window": time_window
        }
        
        # Quality metrics
        quality_stats = {
            "avg_suggestions_per_operation": mean(m.suggestions_generated for m in relevant_metrics),
            "total_conflicts_detected": sum(m.conflicts_detected for m in relevant_metrics),
            "total_conflicts_resolved": sum(m.conflicts_resolved for m in relevant_metrics),
            "total_synergies_found": sum(m.synergies_found for m in relevant_metrics),
            "conflict_resolution_rate": self._calculate_resolution_rate(relevant_metrics)
        }
        
        return {
            "status": "success",
            "performance_stats": performance_stats,
            "quality_stats": quality_stats,
            "system_health": asdict(self.system_health),
            "generated_at": datetime.now().isoformat()
        }
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Get comprehensive usage analytics"""
        return {
            "usage_patterns": asdict(self.usage_analytics),
            "quality_metrics": asdict(self.quality_metrics),
            "trends": self._analyze_usage_trends(),
            "recommendations": self._generate_usage_recommendations()
        }
    
    def get_cost_analysis(self, config) -> Dict[str, Any]:
        """Get cost analysis based on actual usage"""
        if not hasattr(config, 'estimate_monthly_cost'):
            return {"status": "config_not_available"}
        
        # Get actual usage metrics
        recent_metrics = list(self.performance_history)[-100:]  # Last 100 operations
        
        if not recent_metrics:
            return {"status": "insufficient_data"}
        
        # Calculate actual costs
        total_tokens = sum(m.token_usage for m in recent_metrics)
        avg_tokens_per_operation = total_tokens / len(recent_metrics)
        
        # Estimate based on configuration
        estimated_costs = config.estimate_monthly_cost(config)
        
        # Calculate actual vs estimated
        operations_per_day = len([m for m in recent_metrics 
                                if (datetime.now() - m.timestamp).days == 0])
        
        if operations_per_day > 0:
            projected_monthly_ops = operations_per_day * 22  # 22 working days
            projected_monthly_tokens = projected_monthly_ops * avg_tokens_per_operation
            
            # Cost per 1K tokens (approximate)
            cost_per_1k = 0.003  # Claude 3.5 Sonnet pricing
            projected_cost = (projected_monthly_tokens / 1000) * cost_per_1k
            
            return {
                "status": "success",
                "actual_usage": {
                    "avg_tokens_per_operation": avg_tokens_per_operation,
                    "operations_per_day": operations_per_day,
                    "projected_monthly_cost": round(projected_cost, 2),
                    "projected_monthly_tokens": int(projected_monthly_tokens)
                },
                "estimated_usage": estimated_costs,
                "variance": {
                    "cost_difference": round(projected_cost - estimated_costs["estimated_monthly_cost"], 2),
                    "efficiency_ratio": round(estimated_costs["estimated_monthly_cost"] / max(0.01, projected_cost), 2)
                }
            }
        
        return {"status": "insufficient_recent_data"}
    
    def generate_dashboard_report(self) -> str:
        """Generate a comprehensive dashboard report"""
        
        real_time = self.get_real_time_metrics()
        performance = self.get_performance_summary("24h")
        usage = self.get_usage_analytics()
        
        report = f"""
🚀 SuperClaude Code Review System - Performance Dashboard
{'='*60}

📊 REAL-TIME METRICS
{'-'*30}
System Status: {self.system_health.overall_status.upper()}
API Status: {self.system_health.api_status.upper()}
Average Response Time: {real_time.get('current_performance', {}).get('avg_response_time', 0):.3f}s
Success Rate: {self.system_health.success_rate:.1%}
Operations/Minute: {real_time.get('current_performance', {}).get('operations_per_minute', 0):.1f}

⚡ PERFORMANCE (Last 24h)
{'-'*30}
"""
        
        if performance.get('status') == 'success':
            perf_stats = performance['performance_stats']
            quality_stats = performance['quality_stats']
            
            report += f"""Total Operations: {perf_stats['operation_count']}
Response Time (avg): {perf_stats['response_time']['mean']:.3f}s
Response Time (p95): {perf_stats['response_time']['p95']:.3f}s
Token Usage (avg): {perf_stats['token_usage']['mean']:.0f}
Total Tokens: {perf_stats['token_usage']['total']:,}

🎯 QUALITY METRICS
{'-'*30}
Suggestions/Review: {quality_stats['avg_suggestions_per_operation']:.1f}
Conflicts Detected: {quality_stats['total_conflicts_detected']}
Conflicts Resolved: {quality_stats['total_conflicts_resolved']}
Resolution Rate: {quality_stats['conflict_resolution_rate']:.1%}
Synergies Found: {quality_stats['total_synergies_found']}
"""
        
        # Usage patterns
        if usage.get('usage_patterns'):
            patterns = usage['usage_patterns']
            report += f"""
📈 USAGE PATTERNS
{'-'*30}
Most Used Languages: {', '.join(list(patterns.get('language_usage', {}).keys())[:3])}
Peak Usage Hours: {', '.join(patterns.get('peak_usage_times', [])[:3])}
User Engagement: {patterns.get('user_engagement_score', 0):.1f}/10
"""
        
        # System health details
        report += f"""
🏥 SYSTEM HEALTH
{'-'*30}
Collaboration Engine: {self.system_health.collaboration_engine_status.upper()}
Learning Engine: {self.system_health.learning_engine_status.upper()}
Error Rate: {self.system_health.error_rate:.2%}
Last Updated: {self.system_health.last_updated.strftime('%Y-%m-%d %H:%M:%S')}

💡 RECOMMENDATIONS
{'-'*30}
"""
        
        recommendations = usage.get('recommendations', [])
        for i, rec in enumerate(recommendations[:5], 1):
            report += f"{i}. {rec}\n"
        
        if not recommendations:
            report += "System running optimally - no recommendations at this time.\n"
        
        report += f"\n{'='*60}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def _update_system_health(self):
        """Update system health metrics"""
        if len(self.performance_history) < 5:
            return
        
        recent_ops = list(self.performance_history)[-20:]  # Last 20 operations
        
        # Calculate success rate (assuming operations that complete are successful)
        success_rate = 1.0  # Placeholder - would be calculated from actual error tracking
        
        # Calculate average response time
        avg_response = mean(m.response_time for m in recent_ops)
        
        # Determine status based on performance
        if avg_response < 2.0 and success_rate > 0.95:
            status = 'healthy'
        elif avg_response < 5.0 and success_rate > 0.90:
            status = 'degraded'
        else:
            status = 'critical'
        
        self.system_health.overall_status = status
        self.system_health.success_rate = success_rate
        self.system_health.avg_response_time = avg_response
        self.system_health.error_rate = 1.0 - success_rate
        self.system_health.last_updated = datetime.now()
    
    def _update_usage_analytics(self, operation_type: str, metadata: Optional[Dict]):
        """Update usage analytics"""
        now = datetime.now()
        date_key = now.strftime('%Y-%m-%d')
        hour_key = now.hour
        
        # Update daily usage
        if date_key not in self.usage_analytics.daily_reviews:
            self.usage_analytics.daily_reviews[date_key] = 0
        self.usage_analytics.daily_reviews[date_key] += 1
        
        # Update hourly patterns
        if hour_key not in self.usage_analytics.hourly_patterns:
            self.usage_analytics.hourly_patterns[hour_key] = 0
        self.usage_analytics.hourly_patterns[hour_key] += 1
        
        # Update language usage
        if metadata and 'language' in metadata:
            language = metadata['language']
            if language not in self.usage_analytics.language_usage:
                self.usage_analytics.language_usage[language] = 0
            self.usage_analytics.language_usage[language] += 1
    
    def _calculate_ops_per_minute(self) -> float:
        """Calculate operations per minute"""
        if len(self.performance_history) < 2:
            return 0.0
        
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_ops = [m for m in self.performance_history if m.timestamp >= one_minute_ago]
        return len(recent_ops)
    
    def _calculate_resolution_rate(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate conflict resolution rate"""
        total_conflicts = sum(m.conflicts_detected for m in metrics)
        total_resolved = sum(m.conflicts_resolved for m in metrics)
        return total_resolved / max(1, total_conflicts)
    
    def _get_cutoff_time(self, time_window: str) -> datetime:
        """Get cutoff time for time window"""
        now = datetime.now()
        if time_window == "1h":
            return now - timedelta(hours=1)
        elif time_window == "24h":
            return now - timedelta(hours=24)
        elif time_window == "7d":
            return now - timedelta(days=7)
        elif time_window == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default to 24h
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage (placeholder)"""
        # In a real implementation, this would use psutil or similar
        return 0.0
    
    def _analyze_usage_trends(self) -> Dict[str, Any]:
        """Analyze usage trends"""
        return {
            "daily_growth": 0.0,  # Placeholder
            "peak_hours": list(sorted(self.usage_analytics.hourly_patterns.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]),
            "language_trends": dict(sorted(self.usage_analytics.language_usage.items(), 
                                         key=lambda x: x[1], reverse=True)[:5])
        }
    
    def _generate_usage_recommendations(self) -> List[str]:
        """Generate usage recommendations"""
        recommendations = []
        
        # Response time recommendations
        if self.system_health.avg_response_time > 3.0:
            recommendations.append("Consider optimizing API calls or adding caching to improve response times")
        
        # Usage pattern recommendations
        if len(self.usage_analytics.language_usage) > 5:
            recommendations.append("High language diversity detected - consider language-specific optimizations")
        
        # System health recommendations
        if self.system_health.error_rate > 0.05:
            recommendations.append("Error rate above 5% - investigate and improve error handling")
        
        return recommendations
    
    def _background_monitoring(self):
        """Background monitoring and health checks"""
        while self._monitoring_active:
            try:
                # Perform health checks
                self._check_component_health()
                
                # Save metrics periodically
                self._save_metrics_data()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Background monitoring error: {e}")
                time.sleep(60)
    
    def _check_component_health(self):
        """Check health of various components"""
        # Placeholder for actual health checks
        self.system_health.api_status = 'healthy'
        self.system_health.collaboration_engine_status = 'healthy'
        self.system_health.learning_engine_status = 'healthy'
    
    def _load_metrics_data(self):
        """Load historical metrics data"""
        try:
            metrics_file = os.path.join(self.data_dir, "dashboard_metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                
                # Load system health
                if 'system_health' in data:
                    health_data = data['system_health']
                    health_data['last_updated'] = datetime.fromisoformat(health_data['last_updated'])
                    self.system_health = SystemHealth(**health_data)
                
                # Load quality metrics
                if 'quality_metrics' in data:
                    quality_data = data['quality_metrics']
                    quality_data['last_calculated'] = datetime.fromisoformat(quality_data['last_calculated'])
                    self.quality_metrics = QualityMetrics(**quality_data)
                
                # Load usage analytics
                if 'usage_analytics' in data:
                    self.usage_analytics = UsageAnalytics(**data['usage_analytics'])
                
        except Exception as e:
            self.logger.warning(f"Failed to load metrics data: {e}")
    
    def _save_metrics_data(self):
        """Save metrics data to disk"""
        try:
            metrics_file = os.path.join(self.data_dir, "dashboard_metrics.json")
            
            data = {
                'system_health': asdict(self.system_health),
                'quality_metrics': asdict(self.quality_metrics),
                'usage_analytics': asdict(self.usage_analytics),
                'last_saved': datetime.now().isoformat()
            }
            
            # Convert datetime objects to ISO format
            data['system_health']['last_updated'] = self.system_health.last_updated.isoformat()
            data['quality_metrics']['last_calculated'] = self.quality_metrics.last_calculated.isoformat()
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics data: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self._monitoring_active = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)


def create_metrics_dashboard() -> MetricsDashboard:
    """Create a metrics dashboard instance"""
    return MetricsDashboard()


if __name__ == "__main__":
    # Test the metrics dashboard
    dashboard = MetricsDashboard()
    
    # Simulate some operations
    dashboard.record_operation("code_review", 2.5, token_usage=1500, 
                             metadata={"suggestions": 8, "conflicts": 2, "resolved_conflicts": 2})
    dashboard.record_operation("code_review", 1.8, token_usage=1200, 
                             metadata={"suggestions": 5, "conflicts": 1, "resolved_conflicts": 1})
    
    # Generate report
    print(dashboard.generate_dashboard_report())
    
    # Cleanup
    dashboard.cleanup()