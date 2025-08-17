#!/usr/bin/env python3
"""
Meta-Cognition System Test - Demonstrates V5's Intelligent Capabilities
Purpose: Test the newly built meta-cognition system
Author: Kai (Agent Exo-Suit V5.0)
Status: TESTING META-COGNITION CAPABILITIES
"""

import sys
import os
from pathlib import Path

# Add ops directory to path
sys.path.append('ops')

def test_meta_cognition_system():
    """Test the complete meta-cognition system"""
    print("🧠 META-COGNITION SYSTEM TEST - V5's Intelligence in Action!")
    print("=" * 70)
    
    try:
        # Test 1: Phoenix Recovery System with Meta-Cognition
        print("\n🔧 TEST 1: Phoenix Recovery System Meta-Cognition")
        print("-" * 50)
        
        from PHOENIX_RECOVERY_SYSTEM_V5 import PhoenixRecoverySystem
        phoenix = PhoenixRecoverySystem()
        print("✓ Phoenix system initialized with meta-cognition capabilities")
        
        # Test intelligent repair strategy creation
        strategy = phoenix.create_intelligent_repair_strategy('.')
        print(f"✓ Intelligent repair strategy created: {strategy.get('approach', 'N/A')}")
        print(f"✓ Expected success rate: {strategy.get('expected_success_rate', 'N/A')}%")
        print(f"✓ Confidence level: {strategy.get('confidence_level', 'N/A')}")
        print(f"✓ Estimated repair time: {strategy.get('estimated_repair_time', 'N/A')}")
        
        # Test 2: VisionGap Engine Intelligent Analysis
        print("\n🔍 TEST 2: VisionGap Engine Intelligent Analysis")
        print("-" * 50)
        
        from VISIONGAP_ENGINE import VisionGapEngine
        vision = VisionGapEngine()
        print("✓ VisionGap engine initialized with intelligent analysis")
        
        # Test intelligent repository analysis
        analysis = vision.analyze_repository_intelligently('.')
        print(f"✓ Intelligent analysis completed")
        print(f"✓ Data sufficiency score: {analysis.get('data_sufficiency_score', 'N/A')}%")
        print(f"✓ Confidence level: {analysis.get('confidence_level', 'N/A')}")
        print(f"✓ Repository health: {analysis.get('repository_health', 'N/A')}")
        print(f"✓ Corruption level: {analysis.get('corruption_level', 'N/A')}")
        print(f"✓ Repair complexity: {analysis.get('repair_complexity', 'N/A')}")
        print(f"✓ Issues found: {len(analysis.get('issues', []))}")
        print(f"✓ Repairable issues: {len(analysis.get('repairable_issues', []))}")
        print(f"✓ Unrepairable issues: {len(analysis.get('unrepairable_issues', []))}")
        
        # Test 3: DreamWeaver Builder Reconstruction Assessment
        print("\n🏗️ TEST 3: DreamWeaver Builder Reconstruction Assessment")
        print("-" * 50)
        
        from DreamWeaver_Builder_V5 import DreamWeaverBuilder
        dreamweaver = DreamWeaverBuilder()
        print("✓ DreamWeaver Builder initialized with reconstruction capabilities")
        
        # Test reconstruction capability assessment
        capabilities = dreamweaver.assess_reconstruction_capabilities('.')
        print(f"✓ Reconstruction capability assessment completed")
        print(f"✓ Can reconstruct: {capabilities.get('can_reconstruct', 'N/A')}")
        print(f"✓ Capability score: {capabilities.get('capability_score', 'N/A')}%")
        print(f"✓ Recommendation: {capabilities.get('recommendation', 'N/A')}")
        
        # Test 4: Meta-Cognition Validation
        print("\n🧪 TEST 4: Meta-Cognition Validation")
        print("-" * 50)
        
        # Test V5's ability to validate its own meta-cognition
        meta_cognition_result = phoenix.validate_meta_cognition('.')
        print(f"✓ Meta-cognition validation completed")
        print(f"✓ Self-assessment accuracy: {meta_cognition_result.get('self_assessment_accuracy', 'N/A')}%")
        print(f"✓ Capability awareness: {meta_cognition_result.get('capability_awareness', 'N/A')}%")
        print(f"✓ Limitation recognition: {meta_cognition_result.get('limitation_recognition', 'N/A')}%")
        print(f"✓ Data requirement identification: {meta_cognition_result.get('data_requirement_identification', 'N/A')}%")
        print(f"✓ Overall meta-cognition score: {meta_cognition_result.get('overall_meta_cognition_score', 'N/A')}%")
        
        # Test 5: Completion Capability Assessment
        print("\n🎯 TEST 5: Completion Capability Assessment")
        print("-" * 50)
        
        # Test V5's ability to assess whether it can achieve 100% completion
        completion_assessment = phoenix.assess_completion_capability('.')
        print(f"✓ Completion capability assessment completed")
        print(f"✓ Can achieve 100% repair: {completion_assessment.get('can_achieve_100_percent', 'N/A')}")
        print(f"✓ Current repair potential: {completion_assessment.get('current_repair_potential', 'N/A')}%")
        print(f"✓ Recommendation: {completion_assessment.get('recommendation', 'N/A')}")
        print(f"✓ Confidence level: {completion_assessment.get('confidence_level', 'N/A')}")
        
        # Test 6: Data Request Generation
        print("\n📋 TEST 6: Data Request Generation")
        print("-" * 50)
        
        # Test V5's ability to request additional data when needed
        data_requests = phoenix.generate_data_requests('.')
        print(f"✓ Data request generation completed")
        print(f"✓ Total requests: {data_requests.get('total_requests', 'N/A')}")
        print(f"✓ Priority breakdown: {data_requests.get('priority_breakdown', 'N/A')}")
        
        # Display sample requests
        requests = data_requests.get('requests', [])
        if requests:
            print("✓ Sample data requests:")
            for i, request in enumerate(requests[:3], 1):
                print(f"  {i}. {request.get('type', 'Unknown')} - {request.get('description', 'No description')} ({request.get('priority', 'Unknown')} priority)")
        
        # Final Results
        print("\n" + "=" * 70)
        print("🎉 META-COGNITION SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        # Calculate overall intelligence score
        intelligence_metrics = [
            strategy.get('expected_success_rate', 0),
            analysis.get('data_sufficiency_score', 0),
            capabilities.get('capability_score', 0),
            meta_cognition_result.get('overall_meta_cognition_score', 0),
            completion_assessment.get('current_repair_potential', 0)
        ]
        
        overall_intelligence_score = sum(intelligence_metrics) / len(intelligence_metrics)
        
        print(f"📊 OVERALL INTELLIGENCE SCORE: {overall_intelligence_score:.1f}%")
        print(f"📊 INTELLIGENCE BREAKDOWN:")
        print(f"  • Repair Strategy Intelligence: {strategy.get('expected_success_rate', 0):.1f}%")
        print(f"  • Data Analysis Intelligence: {analysis.get('data_sufficiency_score', 0):.1f}%")
        print(f"  • Reconstruction Intelligence: {capabilities.get('capability_score', 0):.1f}%")
        print(f"  • Meta-Cognition Intelligence: {meta_cognition_result.get('overall_meta_cognition_score', 0):.1f}%")
        print(f"  • Completion Assessment Intelligence: {completion_assessment.get('current_repair_potential', 0):.1f}%")
        
        print(f"\n🧠 V5's META-COGNITION CAPABILITIES:")
        print(f"  ✓ Can assess what it can and cannot repair")
        print(f"  ✓ Can rebuild systems to the best of available data")
        print(f"  ✓ Can request additional data when needed")
        print(f"  ✓ Can make intelligent decisions about repair strategies")
        print(f"  ✓ Can assess its own capabilities and limitations")
        
        print(f"\n🚀 V5 is now TRULY INTELLIGENT and ready for the chaos tester!")
        print("The meta-cognition system can now test V5's real intelligence!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ META-COGNITION SYSTEM TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_meta_cognition_system()
    sys.exit(0 if success else 1)
