#!/usr/bin/env python3
"""
Comprehensive demonstration of Enhanced SuperClaude Multi-Agent Code Review System
Showcases all new high-priority features and capabilities
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from SuperClaude.Extensions.CodeReview.config import ConfigManager, get_config
    from SuperClaude.Extensions.CodeReview.utils.metrics_dashboard import MetricsDashboard
    from SuperClaude.Extensions.CodeReview.utils.continuous_learning import ContinuousLearningEngine
    from SuperClaude.Extensions.CodeReview.utils.collaboration_engine import CrossAgentCollaborationEngine
    from SuperClaude.Extensions.CodeReview import get_all_agents, AgentCoordinator
    from SuperClaude.Extensions.CodeReview.agents import CodeSuggestion, SeverityLevel
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class EnhancedFeatureDemo:
    """Comprehensive demonstration of all enhanced features"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.dashboard = MetricsDashboard()
        self.learning_engine = ContinuousLearningEngine()
        
    async def run_comprehensive_demo(self):
        """Run complete demonstration of enhanced features"""
        print("🚀 SuperClaude Enhanced Code Review System - Comprehensive Demo")
        print("=" * 70)
        
        # Demo 1: Cost Calculation & Budget Management
        print("\n💰 DEMO 1: Cost Calculation & Budget Management")
        print("-" * 50)
        await self._demo_cost_calculation()
        
        # Demo 2: Multi-Language Support
        print("\n🌐 DEMO 2: Multi-Language Support")
        print("-" * 50)
        await self._demo_multi_language_support()
        
        # Demo 3: Machine Learning Strategy Selection
        print("\n🧠 DEMO 3: Machine Learning Strategy Selection")
        print("-" * 50)
        await self._demo_ml_strategy_selection()
        
        # Demo 4: Continuous Learning Engine
        print("\n📚 DEMO 4: Continuous Learning Engine")
        print("-" * 50)
        await self._demo_continuous_learning()
        
        # Demo 5: Performance Analytics Dashboard
        print("\n📊 DEMO 5: Performance Analytics Dashboard")
        print("-" * 50)
        await self._demo_performance_dashboard()
        
        # Demo 6: Integrated Code Review with All Features
        print("\n🔗 DEMO 6: Integrated Code Review (All Features)")
        print("-" * 50)
        await self._demo_integrated_review()
        
        print("\n🎉 Demo Complete!")
        print("=" * 70)
    
    async def _demo_cost_calculation(self):
        """Demonstrate cost calculation and budget management"""
        print("Calculating estimated costs based on configuration...")
        
        # Get cost estimate
        cost_analysis = self.config_manager.estimate_monthly_cost(self.config)
        
        print(f"📈 Cost Analysis:")
        print(f"   Team Size: {cost_analysis['team_size']} developers")
        print(f"   Usage Multiplier: {cost_analysis['usage_multiplier']}x")
        print(f"   Estimated Monthly Cost: ${cost_analysis['estimated_monthly_cost']}")
        print(f"   Requests per Month: {cost_analysis['requests_per_month']:,}")
        print(f"   Tokens per Month: {cost_analysis['total_tokens_per_month']:,}")
        print(f"   Cost per Request: ${cost_analysis['cost_per_request']}")
        
        # Budget status
        status_icon = {
            "ok": "✅",
            "warning": "⚠️",
            "over_budget": "🚨"
        }.get(cost_analysis['budget_status'], "❓")
        
        print(f"   Budget Status: {status_icon} {cost_analysis['budget_status'].upper()}")
        print(f"   Budget Utilization: {cost_analysis['budget_utilization']:.1%}")
        
        # Recommendations
        if cost_analysis['budget_status'] == 'over_budget':
            print("💡 Recommendations:")
            print("   • Reduce team size or usage frequency")
            print("   • Switch to Claude Haiku for non-critical reviews")
            print("   • Implement caching to reduce API calls")
        elif cost_analysis['budget_status'] == 'warning':
            print("💡 Recommendations:")
            print("   • Monitor usage closely")
            print("   • Consider usage optimization")
    
    async def _demo_multi_language_support(self):
        """Demonstrate multi-language support"""
        print("Showcasing language-specific configurations...")
        
        # Show supported languages
        language_configs = self.config.agents.language_configs
        
        print(f"🌍 Supported Languages: {len(language_configs)}")
        
        for language, config in list(language_configs.items())[:5]:  # Show first 5
            print(f"\n📝 {language.upper()}:")
            print(f"   Style Guide: {config.style_guide}")
            print(f"   Complexity Threshold: {config.complexity_threshold}")
            print(f"   Line Length: {config.line_length}")
            print(f"   Naming Convention: {config.naming_convention}")
            print(f"   Security Patterns: {len(config.security_patterns)} patterns")
            print(f"   Performance Patterns: {len(config.performance_patterns)} patterns")
            
            # Show sample patterns
            if config.security_patterns:
                print(f"   Sample Security Pattern: {config.security_patterns[0]}")
            if config.performance_patterns:
                print(f"   Sample Performance Pattern: {config.performance_patterns[0]}")
        
        print(f"\n... and {len(language_configs) - 5} more languages supported!")
    
    async def _demo_ml_strategy_selection(self):
        """Demonstrate machine learning strategy selection"""
        print("Testing machine learning-powered conflict resolution...")
        
        # Create collaboration engine
        from SuperClaude.Extensions.CodeReview.utils.collaboration_engine import (
            ProjectContext, ResolutionStrategy
        )
        
        context = ProjectContext(priority="security", security_sensitive=True)
        engine = CrossAgentCollaborationEngine(context)
        
        # Simulate strategy learning
        strategies = list(ResolutionStrategy)
        
        print("🧠 Machine Learning Strategy Selection:")
        print(f"   Available Strategies: {len(strategies)}")
        
        for strategy in strategies[:3]:  # Show first 3
            if strategy in engine.strategy_effectiveness:
                effectiveness = engine.strategy_effectiveness[strategy]
                print(f"   📊 {strategy.value}:")
                print(f"      Success Rate: {effectiveness.success_rate:.1%}")
                print(f"      Total Uses: {effectiveness.total_uses}")
                print(f"      User Rating: {effectiveness.avg_user_rating:.1f}/5.0")
            else:
                print(f"   📊 {strategy.value}: No data yet (will learn from usage)")
        
        # Simulate recording feedback
        print("\n🔄 Simulating strategy feedback recording...")
        engine.record_strategy_feedback(
            "test_conflict_001", 
            ResolutionStrategy.CONTEXT_DRIVEN, 
            success=True, 
            user_rating=4.5
        )
        print("   ✅ Feedback recorded - system will improve over time!")
    
    async def _demo_continuous_learning(self):
        """Demonstrate continuous learning engine"""
        print("Showcasing continuous learning and user feedback integration...")
        
        # Create sample suggestion
        test_suggestion = CodeSuggestion(
            id="demo_001",
            agent_name="Security Agent",
            principle="SQL Injection Prevention",
            line_number=5,
            original_code="query = f\"SELECT * FROM users WHERE id = {user_id}\"",
            suggested_code="query = \"SELECT * FROM users WHERE id = %s\"\nresult = cursor.execute(query, (user_id,))",
            reasoning="String formatting in SQL queries enables SQL injection attacks",
            educational_explanation="SQL injection is critical vulnerability - always use parameterized queries",
            impact_score=9.5,
            confidence=0.95,
            severity=SeverityLevel.CRITICAL,
            category="security"
        )
        
        # Record feedback
        print("📝 Recording user feedback...")
        self.learning_engine.record_feedback(
            suggestion=test_suggestion,
            user_action="accepted",
            user_rating=5.0,
            time_to_decision=15.5,
            context={"language": "python", "file_type": "backend"}
        )
        
        # Get learning insights
        insights = self.learning_engine.get_learning_insights()
        
        print("🧠 Learning Insights:")
        if insights.get('status') == 'active':
            print(f"   Total Feedback Records: {insights['total_feedback_records']}")
            print(f"   Overall Acceptance Rate: {insights['overall_acceptance_rate']:.1%}")
            print(f"   Average User Rating: {insights['average_user_rating']:.1f}/5.0")
            
            # Agent performance
            if insights.get('agent_rankings'):
                print("   🏆 Top Performing Agents:")
                for i, agent in enumerate(insights['agent_rankings'][:3], 1):
                    print(f"      {i}. {agent['agent']}: {agent['acceptance_rate']:.1%} acceptance")
        
        # Show improvement suggestions
        improvements = self.learning_engine.get_improvement_suggestions()
        if improvements:
            print("   💡 System Improvement Suggestions:")
            for improvement in improvements[:2]:
                print(f"      • {improvement['recommendation']}")
    
    async def _demo_performance_dashboard(self):
        """Demonstrate performance analytics dashboard"""
        print("Showcasing real-time performance analytics...")
        
        # Simulate some operations
        print("📊 Recording simulated operations...")
        
        operations = [
            {"type": "code_review", "duration": 2.3, "tokens": 1450, "metadata": {"suggestions": 6, "conflicts": 1, "resolved_conflicts": 1, "language": "python"}},
            {"type": "code_review", "duration": 1.8, "tokens": 1200, "metadata": {"suggestions": 4, "conflicts": 0, "resolved_conflicts": 0, "language": "javascript"}},
            {"type": "code_review", "duration": 3.1, "tokens": 1800, "metadata": {"suggestions": 8, "conflicts": 2, "resolved_conflicts": 2, "language": "java"}},
            {"type": "code_review", "duration": 1.5, "tokens": 900, "metadata": {"suggestions": 3, "conflicts": 0, "resolved_conflicts": 0, "language": "python"}},
        ]
        
        for op in operations:
            self.dashboard.record_operation(
                operation_type=op["type"],
                duration=op["duration"],
                token_usage=op["tokens"],
                metadata=op["metadata"]
            )
        
        # Get real-time metrics
        metrics = self.dashboard.get_real_time_metrics()
        
        if metrics.get('current_performance'):
            perf = metrics['current_performance']
            print("⚡ Real-Time Performance:")
            print(f"   Average Response Time: {perf['avg_response_time']:.2f}s")
            print(f"   Average Token Usage: {perf['avg_token_usage']:.0f}")
            print(f"   Average Suggestions: {perf['avg_suggestions']:.1f}")
            print(f"   Operations/Minute: {perf['operations_per_minute']:.1f}")
        
        # System health
        if metrics.get('system_health'):
            health = metrics['system_health']
            print("🏥 System Health:")
            print(f"   Overall Status: {health['overall_status'].upper()}")
            print(f"   Success Rate: {health['success_rate']:.1%}")
            print(f"   Error Rate: {health['error_rate']:.2%}")
        
        # Performance summary
        summary = self.dashboard.get_performance_summary("1h")
        if summary.get('status') == 'success':
            print("📈 Performance Summary (Last Hour):")
            stats = summary['performance_stats']
            quality = summary['quality_stats']
            print(f"   Total Operations: {stats['operation_count']}")
            print(f"   P95 Response Time: {stats['response_time']['p95']:.2f}s")
            print(f"   Conflict Resolution Rate: {quality['conflict_resolution_rate']:.1%}")
            print(f"   Total Synergies Found: {quality['total_synergies_found']}")
    
    async def _demo_integrated_review(self):
        """Demonstrate integrated code review with all features"""
        print("Running comprehensive code review with all enhanced features...")
        
        # Sample code with multiple issues
        sample_code = '''
def process_user_data(user_input, db_connection):
    # Multiple intentional issues for demonstration
    temp = user_input  # Poor naming
    if temp:
        # SQL injection vulnerability
        query = f"SELECT * FROM users WHERE id = {temp['id']}"
        result = db_connection.execute(query)
        
        # Performance issue - N+1 queries
        for row in result:
            detail_query = f"SELECT * FROM details WHERE user_id = {row['id']}"
            details = db_connection.execute(detail_query)
            print(details)  # Should use logging
        
        return result
    return None  # Inconsistent return types
'''
        
        print("🔍 Analyzing sample code with multiple issues...")
        
        # Get agents and create coordinator
        agents = get_all_agents()
        
        # Enhanced project context
        project_context = {
            'priority': 'security',
            'development_phase': 'production',
            'security_sensitive': True,
            'performance_critical': True,
            'language': 'python'
        }
        
        coordinator = AgentCoordinator(agents, project_context)
        
        # Run comprehensive review
        import time
        start_time = time.time()
        
        results = await coordinator.run_comprehensive_review(
            sample_code, 
            "python", 
            "demo_sample.py"
        )
        
        duration = time.time() - start_time
        
        # Record operation for dashboard
        self.dashboard.record_operation(
            operation_type="integrated_demo",
            duration=duration,
            token_usage=results['summary'].get('total_tokens_used', 0),
            metadata={
                'suggestions': results['summary']['total_suggestions'],
                'conflicts': results['summary'].get('conflicts_detected', 0),
                'resolved_conflicts': results['summary'].get('conflicts_resolved', 0),
                'synergies': results['summary'].get('synergies_found', 0),
                'language': 'python'
            }
        )
        
        # Display results
        print("📋 Comprehensive Review Results:")
        summary = results['summary']
        print(f"   Total Suggestions: {summary['total_suggestions']}")
        print(f"   Conflicts Detected: {summary.get('conflicts_detected', 0)}")
        print(f"   Conflicts Resolved: {summary.get('conflicts_resolved', 0)}")
        print(f"   Synergies Found: {summary.get('synergies_found', 0)}")
        
        if 'collaboration_score' in summary:
            print(f"   Collaboration Score: {summary['collaboration_score']:.1f}/100")
        
        print(f"   Processing Time: {duration:.2f}s")
        
        # Show focus areas
        if results.get('focus_areas'):
            print("🎯 Recommended Focus Areas:")
            for area in results['focus_areas'][:3]:
                print(f"   • {area}")
        
        # Show sample suggestions
        if results.get('agent_results'):
            print("💡 Sample Suggestions:")
            suggestion_count = 0
            for agent_result in results['agent_results']:
                for suggestion in agent_result.suggestions[:2]:  # Show 2 per agent
                    if suggestion_count < 3:  # Max 3 total
                        print(f"   📝 {suggestion.agent_name}: {suggestion.principle}")
                        print(f"      Impact: {suggestion.impact_score}/10 | Confidence: {suggestion.confidence:.1%}")
                        print(f"      {suggestion.reasoning[:80]}...")
                        suggestion_count += 1
        
        print("\n✨ All enhanced features working together seamlessly!")


async def main():
    """Main demo function"""
    demo = EnhancedFeatureDemo()
    await demo.run_comprehensive_demo()
    
    # Cleanup
    demo.dashboard.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)