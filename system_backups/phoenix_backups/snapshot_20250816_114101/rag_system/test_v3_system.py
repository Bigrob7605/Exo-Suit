#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - RAG System Test Suite
Comprehensive testing of all RAG components with CPU/GPU support
"""

import os
import sys
import json
import time
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
try:
    from device_manager import DeviceManager
    from text_processor import TextProcessor
    from embedding_engine import EmbeddingEngine
    from build_index_v3 import RAGIndexBuilder
    from retrieve_v3 import RAGRetriever
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required modules are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGSystemTester:
    """Comprehensive tester for the RAG system V3.0"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.test_files_dir = None
        
        # Test configuration
        self.test_config = {
            'chunk_size': 256,
            'chunk_overlap': 25,
            'model_name': 'all-MiniLM-L6-v2',
            'device_mode': 'auto',
            'batch_size': 16
        }
    
    def setup_test_environment(self):
        """Create test files and environment"""
        logger.info("Setting up test environment...")
        
        try:
            # Create temporary test directory
            self.test_files_dir = tempfile.mkdtemp(prefix="rag_test_")
            logger.info(f"Test directory created: {self.test_files_dir}")
            
            # Create test files
            self._create_test_files()
            
            logger.info("Test environment setup completed")
            
        except Exception as e:
            logger.error(f"Test environment setup failed: {e}")
            raise
    
    def _create_test_files(self):
        """Create various test files for comprehensive testing"""
        test_files = {
            'test_python.py': '''#!/usr/bin/env python3
"""
Test Python file for RAG system testing
This file contains various Python code patterns and documentation.
"""

import os
import sys
from typing import List, Dict, Any

class TestClass:
    """A test class for demonstration purposes."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_data(self, item: Any) -> None:
        """Add an item to the data list."""
        self.data.append(item)
    
    def get_data(self) -> List[Any]:
        """Get all data items."""
        return self.data.copy()

def test_function(param: str) -> str:
    """A test function that returns a modified parameter."""
    return f"Processed: {param}"

if __name__ == "__main__":
    # Test the functionality
    obj = TestClass("test")
    obj.add_data("sample data")
    result = test_function("hello world")
    print(result)
''',
            
            'test_markdown.md': '''# Test Markdown Document

This is a test markdown file for the RAG system.

## Features

- **Bold text** and *italic text*
- Lists and sublists
- Code blocks and inline code
- Links and references

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Conclusion

This document tests various markdown features.
''',
            
            'test_json.json': '''{
    "name": "Test Configuration",
    "version": "1.0.0",
    "description": "A test configuration file",
    "settings": {
        "enabled": true,
        "timeout": 30,
        "retries": 3
    },
    "features": [
        "feature1",
        "feature2",
        "feature3"
    ]
}''',
            
            'test_yaml.yaml': '''# Test YAML Configuration
name: Test App
version: 2.0.0
description: Test application configuration

database:
  host: localhost
  port: 5432
  name: testdb

features:
  - authentication
  - logging
  - monitoring

settings:
  debug: false
  log_level: INFO
''',
            
            'test_text.txt': '''This is a plain text file for testing the RAG system.

It contains various types of content including:
- Technical information
- Documentation snippets
- Code examples
- Configuration details

The system should be able to process this file and extract meaningful chunks for indexing and retrieval.

This file tests the text processing capabilities including:
1. Chunking algorithms
2. Text cleaning
3. Unicode handling
4. Emoji removal (if any emojis are present)

End of test file.
'''
        }
        
        # Create test files
        for filename, content in test_files.items():
            file_path = os.path.join(self.test_files_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.debug(f"Created test file: {filename}")
    
    def test_device_manager(self) -> Dict[str, Any]:
        """Test the device manager component"""
        logger.info("Testing Device Manager...")
        
        test_result = {
            'component': 'DeviceManager',
            'status': 'failed',
            'tests': {},
            'errors': []
        }
        
        try:
            # Create device manager
            device_manager = DeviceManager(self.test_config)
            
            # Test system detection
            test_result['tests']['system_detection'] = 'passed'
            
            # Test requirements validation
            requirements_ok, missing_packages = device_manager.validate_requirements()
            test_result['tests']['requirements_validation'] = 'passed' if requirements_ok else 'partial'
            if missing_packages:
                test_result['tests']['missing_packages'] = missing_packages
            
            # Test configuration generation
            config = device_manager.get_optimal_configuration()
            test_result['tests']['configuration_generation'] = 'passed'
            test_result['tests']['optimal_config'] = config
            
            # Test system summary
            summary = device_manager.get_system_summary()
            test_result['tests']['system_summary'] = 'passed'
            test_result['tests']['summary'] = summary
            
            test_result['status'] = 'passed'
            logger.info("Device Manager tests passed")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"Device Manager test failed: {e}")
        
        return test_result
    
    def test_text_processor(self) -> Dict[str, Any]:
        """Test the text processor component"""
        logger.info("Testing Text Processor...")
        
        test_result = {
            'component': 'TextProcessor',
            'status': 'failed',
            'tests': {},
            'errors': []
        }
        
        try:
            # Create text processor
            processor = TextProcessor(
                chunk_size=self.test_config['chunk_size'],
                chunk_overlap=self.test_config['chunk_overlap']
            )
            
            # Test text cleaning
            test_text = "Hello! This is a test with Unicode "
            cleaned_text = processor.clean_text(test_text)
            test_result['tests']['text_cleaning'] = 'passed'
            test_result['tests']['cleaned_text'] = cleaned_text
            
            # Test text chunking
            long_text = "This is a long text. " * 50
            chunks = processor.chunk_text(long_text)
            test_result['tests']['text_chunking'] = 'passed'
            test_result['tests']['chunk_count'] = len(chunks)
            test_result['tests']['chunk_sizes'] = [len(chunk) for chunk in chunks[:3]]
            
            # Test file processing
            test_file = os.path.join(self.test_files_dir, 'test_text.txt')
            if os.path.exists(test_file):
                file_chunks = processor.process_file(test_file)
                test_result['tests']['file_processing'] = 'passed'
                test_result['tests']['file_chunks'] = len(file_chunks)
            
            # Test batch processing
            test_files = [os.path.join(self.test_files_dir, f) for f in os.listdir(self.test_files_dir)]
            test_files = [f for f in test_files if os.path.isfile(f)]
            
            if test_files:
                batch_chunks = processor.process_files_batch(test_files[:3])
                test_result['tests']['batch_processing'] = 'passed'
                test_result['tests']['batch_chunks'] = len(batch_chunks)
            
            test_result['status'] = 'passed'
            logger.info("Text Processor tests passed")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"Text Processor test failed: {e}")
        
        return test_result
    
    def test_embedding_engine(self) -> Dict[str, Any]:
        """Test the embedding engine component"""
        logger.info("Testing Embedding Engine...")
        
        test_result = {
            'component': 'EmbeddingEngine',
            'status': 'failed',
            'tests': {},
            'errors': []
        }
        
        try:
            # Create embedding engine
            engine = EmbeddingEngine(
                model_name=self.test_config['model_name'],
                device_mode=self.test_config['device_mode'],
                batch_size=self.test_config['batch_size']
            )
            
            # Test embedding generation
            test_texts = [
                "This is a test sentence for embedding generation.",
                "Another test sentence to verify the system works.",
                "Testing the embedding engine with multiple sentences."
            ]
            
            embeddings = engine.generate_embeddings(test_texts)
            test_result['tests']['embedding_generation'] = 'passed'
            test_result['tests']['embedding_shape'] = embeddings.shape
            test_result['tests']['embedding_sample'] = embeddings[0][:5].tolist()
            
            # Test FAISS index creation
            index = engine.create_faiss_index(embeddings)
            test_result['tests']['faiss_index_creation'] = 'passed'
            test_result['tests']['index_vectors'] = index.ntotal
            
            # Test performance stats
            stats = engine.get_performance_stats()
            test_result['tests']['performance_stats'] = 'passed'
            test_result['tests']['stats'] = stats
            
            test_result['status'] = 'passed'
            logger.info("Embedding Engine tests passed")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"Embedding Engine test failed: {e}")
        
        return test_result
    
    def test_index_building(self) -> Dict[str, Any]:
        """Test the index building pipeline"""
        logger.info("Testing Index Building Pipeline...")
        
        test_result = {
            'component': 'IndexBuilding',
            'status': 'failed',
            'tests': {},
            'errors': []
        }
        
        try:
            # Create index builder
            builder = RAGIndexBuilder(self.test_config)
            
            # Test file discovery
            discovered_files = builder.discover_files([self.test_files_dir])
            test_result['tests']['file_discovery'] = 'passed'
            test_result['tests']['discovered_files'] = len(discovered_files)
            
            # Test file processing
            chunks = builder.process_files(discovered_files)
            test_result['tests']['file_processing'] = 'passed'
            test_result['tests']['total_chunks'] = len(chunks)
            
            # Test index building
            output_dir = os.path.join(self.test_files_dir, 'rag_output')
            output_paths = builder.build_index(chunks, output_dir)
            test_result['tests']['index_building'] = 'passed'
            test_result['tests']['output_paths'] = output_paths
            
            # Verify output files
            for path_type, path in output_paths.items():
                if os.path.exists(path):
                    test_result['tests'][f'{path_type}_exists'] = 'passed'
                else:
                    test_result['tests'][f'{path_type}_exists'] = 'failed'
            
            test_result['status'] = 'passed'
            logger.info("Index Building tests passed")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"Index Building test failed: {e}")
        
        return test_result
    
    def test_retrieval(self) -> Dict[str, Any]:
        """Test the retrieval system"""
        logger.info("Testing Retrieval System...")
        
        test_result = {
            'component': 'Retrieval',
            'status': 'failed',
            'tests': {},
            'errors': []
        }
        
        try:
            # Find the output directory
            rag_output_dir = os.path.join(self.test_files_dir, 'rag_output')
            if not os.path.exists(rag_output_dir):
                test_result['errors'].append("RAG output directory not found")
                return test_result
            
            # Create retriever
            retriever = RAGRetriever(rag_output_dir, self.test_config)
            
            # Test index loading
            test_result['tests']['index_loading'] = 'passed'
            
            # Test search functionality
            test_queries = [
                "Python class definition",
                "markdown features",
                "configuration settings",
                "text processing"
            ]
            
            search_results = []
            for query in test_queries:
                results = retriever.search(query, top_k=3)
                search_results.append({
                    'query': query,
                    'results_count': len(results),
                    'top_score': results[0]['similarity_score'] if results else 0
                })
            
            test_result['tests']['search_functionality'] = 'passed'
            test_result['tests']['search_results'] = search_results
            
            # Test index statistics
            stats = retriever.get_index_stats()
            test_result['tests']['index_statistics'] = 'passed'
            test_result['tests']['statistics'] = stats
            
            test_result['status'] = 'passed'
            logger.info("Retrieval tests passed")
            
        except Exception as e:
            test_result['errors'].append(str(e))
            logger.error(f"Retrieval test failed: {e}")
        
        return test_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        logger.info("Starting comprehensive RAG system tests...")
        
        self.start_time = time.time()
        
        # Run all test components
        test_components = [
            ('device_manager', self.test_device_manager),
            ('text_processor', self.test_text_processor),
            ('embedding_engine', self.test_embedding_engine),
            ('index_building', self.test_index_building),
            ('retrieval', self.test_retrieval)
        ]
        
        for component_name, test_func in test_components:
            logger.info(f"Testing {component_name}...")
            try:
                result = test_func()
                self.test_results[component_name] = result
            except Exception as e:
                logger.error(f"Test {component_name} failed with exception: {e}")
                self.test_results[component_name] = {
                    'component': component_name,
                    'status': 'failed',
                    'errors': [str(e)]
                }
        
        # Generate overall report
        overall_result = self._generate_overall_report()
        
        return overall_result
    
    def _generate_overall_report(self) -> Dict[str, Any]:
        """Generate overall test report"""
        total_time = time.time() - self.start_time
        
        # Count test results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        # Overall status
        overall_status = 'passed' if failed_tests == 0 else 'partial' if passed_tests > 0 else 'failed'
        
        report = {
            'test_summary': {
                'overall_status': overall_status,
                'total_components': total_tests,
                'passed_components': passed_tests,
                'failed_components': failed_tests,
                'total_time_seconds': total_time
            },
            'component_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for common issues
        if any('requirements' in result.get('tests', {}) and 
               result['tests']['requirements'] == 'partial' 
               for result in self.test_results.values()):
            recommendations.append("Install missing Python packages for full functionality")
        
        if any(result['status'] == 'failed' for result in self.test_results.values()):
            recommendations.append("Review failed component tests for specific issues")
        
        if not recommendations:
            recommendations.append("All tests passed! System is ready for production use.")
        
        return recommendations
    
    def print_test_report(self, report: Dict[str, Any]):
        """Print formatted test report"""
        print("\n" + "="*80)
        print("AGENT EXO-SUIT V3.0 - RAG SYSTEM TEST REPORT")
        print("="*80)
        
        # Summary
        summary = report['test_summary']
        print(f"\nTEST SUMMARY")
        print(f"   Overall Status: {summary['overall_status'].upper()}")
        print(f"   Components Tested: {summary['total_components']}")
        print(f"   Passed: {summary['passed_components']}")
        print(f"   Failed: {summary['failed_components']}")
        print(f"   Total Time: {summary['total_time_seconds']:.2f} seconds")
        
        # Component results
        print(f"\n COMPONENT RESULTS")
        for component_name, result in report['component_results'].items():
            status_icon = "OK" if result['status'] == 'passed' else "FAILED" if result['status'] == 'failed' else "WARNING"
            print(f"   {status_icon} {component_name}: {result['status']}")
            
            if result.get('errors'):
                for error in result['errors']:
                    print(f"      Error: {error}")
        
        # Recommendations
        print(f"\n RECOMMENDATIONS")
        for rec in report['recommendations']:
            print(f"    {rec}")
        
        print("="*80)
    
    def cleanup(self):
        """Clean up test environment"""
        if self.test_files_dir and os.path.exists(self.test_files_dir):
            try:
                shutil.rmtree(self.test_files_dir)
                logger.info("Test environment cleaned up")
            except Exception as e:
                logger.warning(f"Failed to cleanup test environment: {e}")


def main():
    """Main test function"""
    print(" Starting Agent Exo-Suit V3.0 RAG System Tests...")
    
    tester = RAGSystemTester()
    
    try:
        # Setup test environment
        tester.setup_test_environment()
        
        # Run all tests
        report = tester.run_all_tests()
        
        # Print results
        tester.print_test_report(report)
        
        # Save detailed report
        report_file = "rag_system_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n Detailed report saved to: {report_file}")
        
        # Return exit code
        if report['test_summary']['overall_status'] == 'passed':
            print("\n All tests passed! RAG system is working correctly.")
            return 0
        elif report['test_summary']['overall_status'] == 'partial':
            print("\n  Some tests failed. Check the report for details.")
            return 1
        else:
            print("\n All tests failed. System needs attention.")
            return 2
            
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n Test suite failed: {e}")
        return 3
        
    finally:
        # Cleanup
        tester.cleanup()


if __name__ == "__main__":
    exit(main())
