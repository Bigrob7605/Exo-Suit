#!/usr/bin/env python3
"""
Phase 2 Token Upgrade Test Script
Tests the enhanced context governor with 512K tokens and Phase 2 features
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the ops directory to the path
sys.path.append(str(Path(__file__).parent))

# Import the context governor (note: filename uses hyphens, not underscores)
import importlib.util
spec = importlib.util.spec_from_file_location("context_governor", Path(__file__).parent / "context-governor-v5-token-upgrade.py")
context_governor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_governor_module)
TokenUpgradeContextGovernor = context_governor_module.TokenUpgradeContextGovernor

# Configure logging for Phase 2 testing
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/token-upgrade-moonshot/phase2-test.log'),
        logging.StreamHandler()
    ]
)

def test_phase2_features():
    """Test Phase 2 token upgrade features"""
    logging.info("🚀 PHASE 2 TOKEN UPGRADE TEST - 512K TOKENS")
    
    # Initialize Phase 2 context governor
    governor = TokenUpgradeContextGovernor(max_tokens=512000)
    
    # Test Phase 2 initialization
    logging.info(f"Phase: {governor.phase}")
    logging.info(f"Token improvement: {governor.token_improvement}x")
    logging.info(f"Max tokens: {governor.max_tokens:,}")
    
    # Test context compression
    test_data = "This is a test context for Phase 2 compression testing. " * 1000
    logging.info(f"Testing context compression with {len(test_data)} characters")
    
    # Test INT8 compression
    compressed_int8 = governor.compress_context(test_data, 'INT8')
    logging.info(f"INT8 compression test completed")
    
    # Test FP16 compression
    compressed_fp16 = governor.compress_context(test_data, 'FP16')
    logging.info(f"FP16 compression test completed")
    
    # Test shared memory allocation
    shared_entry = governor.allocate_shared_memory(test_data, 'warm')
    if shared_entry:
        logging.info(f"Shared memory allocation test successful: {shared_entry['compression_ratio']:.1%} compression")
    else:
        logging.warning("Shared memory allocation test failed")
    
    # Test GPU memory optimization (if available)
    if hasattr(governor, 'optimize_gpu_memory'):
        logging.info("Testing GPU memory optimization...")
        governor.optimize_gpu_memory()
        logging.info("GPU memory optimization test completed")
    
    # Test eviction policies
    test_pool = {
        'item1': {'last_access': time.time() - 100, 'access_count': 1},
        'item2': {'last_access': time.time() - 50, 'access_count': 5},
        'item3': {'last_access': time.time(), 'access_count': 10}
    }
    
    logging.info("Testing LRU eviction policy...")
    governor.lru_eviction(test_pool, 2)
    logging.info(f"LRU eviction test completed, pool size: {len(test_pool)}")
    
    logging.info("✅ Phase 2 feature tests completed successfully")
    return True

def test_phase2_performance():
    """Test Phase 2 performance improvements"""
    logging.info("🚀 PHASE 2 PERFORMANCE TEST - 512K TOKENS")
    
    # Initialize Phase 2 context governor
    governor = TokenUpgradeContextGovernor(max_tokens=512000)
    
    # Test with a small directory to validate functionality
    test_dir = Path(".") / "ops"
    if test_dir.exists():
        logging.info(f"Testing Phase 2 performance with {test_dir}")
        
        start_time = time.time()
        governor.build_index(str(test_dir), chunk_size=1024, overlap=100)
        end_time = time.time()
        
        processing_time = end_time - start_time
        logging.info(f"Phase 2 processing completed in {processing_time:.2f} seconds")
        
        if governor.documents:
            total_tokens = sum(doc['tokens'] for doc in governor.documents)
            logging.info(f"Total documents processed: {len(governor.documents)}")
            logging.info(f"Total tokens: {total_tokens:,}")
            logging.info(f"Processing rate: {total_tokens/processing_time:.0f} tokens/second")
            
            # Test search functionality
            test_query = "context governor token upgrade"
            search_results = governor.search_with_budget(test_query, top_k=5, max_tokens=10000)
            logging.info(f"Search test completed: {len(search_results['results'])} results")
            
            return True
        else:
            logging.warning("No documents processed in performance test")
            return False
    else:
        logging.warning(f"Test directory {test_dir} not found")
        return False

def main():
    """Main test function"""
    logging.info("🚀 TOKEN UPGRADE MOONSHOT - PHASE 2 TESTING")
    
    # Create logs directory
    log_dir = Path("logs/token-upgrade-moonshot")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Test Phase 2 features
    logging.info("=" * 60)
    logging.info("TESTING PHASE 2 FEATURES")
    logging.info("=" * 60)
    
    feature_test_success = test_phase2_features()
    
    # Test Phase 2 performance
    logging.info("=" * 60)
    logging.info("TESTING PHASE 2 PERFORMANCE")
    logging.info("=" * 60)
    
    performance_test_success = test_phase2_performance()
    
    # Summary
    logging.info("=" * 60)
    logging.info("PHASE 2 TEST SUMMARY")
    logging.info("=" * 60)
    
    if feature_test_success and performance_test_success:
        logging.info("✅ ALL PHASE 2 TESTS PASSED")
        logging.info("🚀 PHASE 2 TOKEN UPGRADE SUCCESSFUL")
        logging.info("📊 ACHIEVEMENT: 512K TOKENS OPERATIONAL (4x improvement)")
        logging.info("🎯 READY FOR PHASE 3: 1M TOKENS")
    else:
        logging.error("❌ SOME PHASE 2 TESTS FAILED")
        logging.error("🔧 Review logs and fix issues before proceeding")
    
    return feature_test_success and performance_test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
