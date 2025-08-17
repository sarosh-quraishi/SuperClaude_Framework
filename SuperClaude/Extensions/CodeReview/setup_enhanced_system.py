#!/usr/bin/env python3
"""
Setup script for Enhanced SuperClaude Multi-Agent Code Review System
Configures the system with Claude API integration and collaboration engine
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from SuperClaude.Extensions.CodeReview.config import ConfigManager, setup_logging, CodeReviewConfig
    from SuperClaude.Extensions.CodeReview.utils.claude_api_integration import test_api_integration
    from SuperClaude.Extensions.CodeReview import get_all_agents, AgentCoordinator
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class EnhancedSystemSetup:
    """Setup and validation for the enhanced code review system"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.setup_results = {}
        
    async def run_complete_setup(self):
        """Run complete setup and validation"""
        print("🚀 Enhanced SuperClaude Code Review System Setup")
        print("=" * 60)
        
        # Step 1: Configuration setup
        print("\n📋 Step 1: Configuration Setup")
        await self._setup_configuration()
        
        # Step 2: Claude API validation  
        print("\n🤖 Step 2: Claude API Integration Test")
        await self._test_claude_api()
        
        # Step 3: Collaboration engine validation
        print("\n🤝 Step 3: Collaboration Engine Test")
        await self._test_collaboration_engine()
        
        # Step 4: Agent system validation
        print("\n👥 Step 4: Multi-Agent System Test")
        await self._test_agent_system()
        
        # Step 5: Integration test
        print("\n🔗 Step 5: End-to-End Integration Test")
        await self._test_integration()
        
        # Step 6: Generate setup report
        print("\n📊 Step 6: Setup Report")
        self._generate_setup_report()
    
    async def _setup_configuration(self):
        """Setup and validate configuration"""
        try:
            # Load or create configuration
            config = self.config_manager.load_config()
            setup_logging(config)
            
            # Validate configuration
            issues = self.config_manager.validate_config(config)
            
            if issues:
                print(f"⚠️  Configuration has {len(issues)} issues:")
                for issue in issues:
                    print(f"   - {issue}")
                self.setup_results['configuration'] = {'status': 'warning', 'issues': issues}
            else:
                print("✅ Configuration is valid")
                self.setup_results['configuration'] = {'status': 'success', 'issues': []}
            
            print(f"   📁 Config file: {self.config_manager.config_path}")
            print(f"   🔑 API Key: {'✅ Configured' if config.claude_api.api_key else '❌ Missing'}")
            print(f"   🤖 Agents: {len(config.agents.enabled_agents)} enabled")
            print(f"   🤝 Collaboration: {'✅ Enabled' if config.enable_collaboration_engine else '❌ Disabled'}")
            
        except Exception as e:
            print(f"❌ Configuration setup failed: {e}")
            self.setup_results['configuration'] = {'status': 'error', 'error': str(e)}
    
    async def _test_claude_api(self):
        """Test Claude API integration"""
        try:
            # Test API connectivity and authentication
            config = self.config_manager.load_config()
            
            if not config.claude_api.api_key:
                print("⚠️  Claude API key not configured")
                print("   Set ANTHROPIC_API_KEY environment variable to enable real analysis")
                self.setup_results['claude_api'] = {'status': 'warning', 'message': 'API key not configured'}
                return
            
            # Test actual API call
            print("   Testing API connectivity...")
            await test_api_integration()
            
            print("✅ Claude API integration working")
            self.setup_results['claude_api'] = {'status': 'success'}
            
        except Exception as e:
            print(f"⚠️  Claude API test failed: {e}")
            print("   System will use mock analysis as fallback")
            self.setup_results['claude_api'] = {'status': 'fallback', 'error': str(e)}
    
    async def _test_collaboration_engine(self):
        """Test collaboration engine functionality"""
        try:
            from SuperClaude.Extensions.CodeReview.utils.collaboration_engine import (
                CrossAgentCollaborationEngine, ProjectContext, create_default_project_context
            )
            
            # Create test collaboration engine
            context = create_default_project_context()
            engine = CrossAgentCollaborationEngine(context)
            
            print("✅ Collaboration engine initialized")
            print(f"   📊 Project context: {context.priority} priority")
            print(f"   🔧 Agent hierarchy: {len(engine.agent_hierarchy)} agents")
            
            self.setup_results['collaboration_engine'] = {'status': 'success'}
            
        except Exception as e:
            print(f"❌ Collaboration engine test failed: {e}")
            self.setup_results['collaboration_engine'] = {'status': 'error', 'error': str(e)}
    
    async def _test_agent_system(self):
        """Test multi-agent system"""
        try:
            # Get all agents
            agents = get_all_agents()
            
            print(f"✅ Agent system loaded: {len(agents)} agents")
            for agent in agents:
                print(f"   🤖 {agent.name}: {len(agent.specializations)} specializations")
            
            # Test agent coordinator
            coordinator = AgentCoordinator(agents)
            print("✅ Agent coordinator initialized")
            
            self.setup_results['agent_system'] = {
                'status': 'success',
                'agent_count': len(agents),
                'agents': [agent.name for agent in agents]
            }
            
        except Exception as e:
            print(f"❌ Agent system test failed: {e}")
            self.setup_results['agent_system'] = {'status': 'error', 'error': str(e)}
    
    async def _test_integration(self):
        """Test end-to-end integration"""
        try:
            # Test with sample code
            test_code = '''
def process_user_data(user_input):
    # Test code with intentional issues
    temp = user_input  # Poor naming
    if temp:
        print(temp)  # Should use logging
    return temp
'''
            
            print("   Running end-to-end analysis...")
            
            # Get agents and coordinator
            agents = get_all_agents()
            
            # Use enhanced coordinator with collaboration engine
            config = self.config_manager.load_config()
            project_context = {
                'priority': config.project.priority,
                'development_phase': config.project.development_phase,
                'performance_critical': config.project.performance_critical,
                'security_sensitive': config.project.security_sensitive
            }
            
            coordinator = AgentCoordinator(agents, project_context)
            
            # Run comprehensive review
            results = await coordinator.run_comprehensive_review(test_code, "python", "test.py")
            
            # Validate results
            total_suggestions = results['summary']['total_suggestions']
            conflicts_detected = results['summary'].get('conflicts_detected', 0)
            collaboration_score = results['summary'].get('collaboration_score', 0)
            
            print(f"✅ Integration test successful")
            print(f"   📝 Generated {total_suggestions} suggestions")
            print(f"   ⚡ Detected {conflicts_detected} conflicts")
            
            if 'collaboration_score' in results['summary']:
                print(f"   🤝 Collaboration score: {collaboration_score:.1f}/100")
                print(f"   🎯 Enhanced features: Active")
            else:
                print(f"   🎯 Enhanced features: Using fallback mode")
            
            self.setup_results['integration'] = {
                'status': 'success',
                'suggestions': total_suggestions,
                'conflicts': conflicts_detected,
                'enhanced_features': 'collaboration_score' in results['summary']
            }
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.setup_results['integration'] = {'status': 'error', 'error': str(e)}
    
    def _generate_setup_report(self):
        """Generate comprehensive setup report"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED SYSTEM SETUP REPORT")
        print("=" * 60)
        
        # Overall status
        failed_components = [k for k, v in self.setup_results.items() if v['status'] == 'error']
        warning_components = [k for k, v in self.setup_results.items() if v['status'] in ['warning', 'fallback']]
        
        if not failed_components:
            if not warning_components:
                print("🎉 ALL SYSTEMS OPERATIONAL")
                print("   Enhanced SuperClaude Code Review System is fully functional!")
            else:
                print("⚠️  SYSTEM OPERATIONAL WITH WARNINGS")
                print("   Core functionality available, some features may be limited")
        else:
            print("❌ SYSTEM SETUP INCOMPLETE")
            print("   Some components failed to initialize")
        
        # Component status
        print(f"\n📋 Component Status:")
        
        status_icons = {
            'success': '✅',
            'warning': '⚠️',
            'fallback': '🔄',
            'error': '❌'
        }
        
        for component, result in self.setup_results.items():
            icon = status_icons.get(result['status'], '❓')
            print(f"   {icon} {component.replace('_', ' ').title()}: {result['status'].title()}")
            
            if 'error' in result:
                print(f"      Error: {result['error']}")
            elif 'issues' in result and result['issues']:
                print(f"      Issues: {len(result['issues'])} configuration issues")
            elif 'message' in result:
                print(f"      Note: {result['message']}")
        
        # Feature availability
        print(f"\n🚀 Enhanced Features:")
        claude_available = self.setup_results.get('claude_api', {}).get('status') == 'success'
        collab_available = self.setup_results.get('collaboration_engine', {}).get('status') == 'success'
        
        print(f"   {'✅' if claude_available else '🔄'} Real Claude AI Analysis: {'Available' if claude_available else 'Fallback to mock analysis'}")
        print(f"   {'✅' if collab_available else '❌'} Intelligent Conflict Resolution: {'Available' if collab_available else 'Basic conflict detection only'}")
        print(f"   {'✅' if claude_available and collab_available else '🔄'} Cross-Agent Collaboration: {'Full functionality' if claude_available and collab_available else 'Limited functionality'}")
        
        # Usage instructions
        print(f"\n📚 Getting Started:")
        if claude_available and collab_available:
            print("   Your enhanced system is ready! Try these commands:")
            print("   • /sc:code_review [file_path] - Comprehensive multi-agent review")
            print("   • /sc:interactive_review [file_path] - Interactive diff-style review")
        elif not claude_available:
            print("   To enable full functionality:")
            print("   1. Set ANTHROPIC_API_KEY environment variable")
            print("   2. Run this setup script again")
            print("   • Current: Mock analysis mode (for testing)")
        
        # Configuration file location
        print(f"\n⚙️  Configuration:")
        print(f"   📁 Config file: {self.config_manager.config_path}")
        print(f"   📝 Edit configuration to customize behavior")
        
        print("\n" + "=" * 60)


async def main():
    """Main setup function"""
    setup = EnhancedSystemSetup()
    await setup.run_complete_setup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)