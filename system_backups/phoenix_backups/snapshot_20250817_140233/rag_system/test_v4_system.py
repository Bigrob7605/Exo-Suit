# Agent Exo-Suit V4.0 - Comprehensive System Test Suite
# Tests all GPU components with the test folder for Windows compatibility

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class V4SystemTester:
    """Comprehensive V4.0 system tester for GPU components"""
    
    def __init__(self, test_folder: str = "../test-emoji-pack"):
        self.test_folder = test_folder
        self.test_results = {}
        self.start_time = time.time()
        
        # Test configuration
        self.test_config = {
            'test_folder': test_folder,
            'supported_extensions': ['.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.txt', '.ps1', '.cs', '.java', '.rb', '.go', '.rs', '.sql', '.psm1', '.vbs'],
            'max_files': 20,  # Limit for testing
            'chunk_size': 512,
            'chunk_overlap': 50
        }
        
        logger.info(f"V4.0 System Tester initialized for folder: {test_folder}")
    
    def test_system_requirements(self) -> Dict[str, Any]:
        """Test system requirements and dependencies"""
        logger.info("Testing system requirements...")
        
        results = {
            'python_version': sys.version,
            'platform': sys.platform,
            'dependencies': {},
            'gpu_available': False,
            'cuda_available': False
        }
        
        # Test core dependencies
        try:
            import numpy as np
            results['dependencies']['numpy'] = {'version': np.__version__, 'status': 'OK'}
        except ImportError as e:
            results['dependencies']['numpy'] = {'status': 'FAILED', 'error': str(e)}
        
        try:
            import torch
            results['dependencies']['torch'] = {'version': torch.__version__, 'status': 'OK'}
            
            # Test CUDA availability
            if torch.cuda.is_available():
                results['cuda_available'] = True
                results['gpu_available'] = True
                results['gpu_info'] = {
                    'device_count': torch.cuda.device_count(),
                    'device_name': torch.cuda.get_device_name(0),
                    'cuda_version': torch.version.cuda
                }
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                logger.info("CUDA not available, using CPU mode")
                
        except ImportError as e:
            results['dependencies']['torch'] = {'status': 'FAILED', 'error': str(e)}
        
        try:
            from sentence_transformers import SentenceTransformer
            results['dependencies']['sentence_transformers'] = {'status': 'OK'}
        except ImportError as e:
            results['dependencies']['sentence_transformers'] = {'status': 'FAILED', 'error': str(e)}
        
        try:
            import faiss
            results['dependencies']['faiss'] = {'status': 'OK'}
        except ImportError as e:
            results['dependencies']['faiss'] = {'status': 'FAILED', 'error': str(e)}
        
        return results
    
    def test_folder_structure(self) -> Dict[str, Any]:
        """Test the test folder structure and file discovery"""
        logger.info(f"Testing folder structure: {self.test_folder}")
        
        results = {
            'folder_exists': False,
            'file_count': 0,
            'supported_files': [],
            'unsupported_files': [],
            'total_size': 0
        }
        
        if not os.path.exists(self.test_folder):
            logger.error(f"Test folder not found: {self.test_folder}")
            return results
        
        results['folder_exists'] = True
        
        # Discover files
        for root, dirs, files in os.walk(self.test_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in self.test_config['supported_extensions']:
                    results['supported_files'].append({
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'extension': file_ext
                    })
                    results['total_size'] += os.path.getsize(file_path)
                else:
                    results['unsupported_files'].append({
                        'path': file_path,
                        'extension': file_ext
                    })
        
        results['file_count'] = len(results['supported_files'])
        logger.info(f"Found {results['file_count']} supported files ({results['total_size']} bytes)")
        
        return results
    
    def test_gpu_embeddings(self) -> Dict[str, Any]:
        """Test GPU-accelerated embedding generation"""
        logger.info("Testing GPU embeddings...")
        
        results = {
            'status': 'FAILED',
            'device_used': 'unknown',
            'processing_time': 0,
            'embedding_count': 0,
            'embedding_dimension': 0,
            'error': None
        }
        
        try:
            import torch
            from sentence_transformers import SentenceTransformer
            
            if not torch.cuda.is_available():
                logger.info("CUDA not available, testing CPU embeddings")
                device = 'cpu'
                results['device_used'] = 'cpu'
            else:
                device = 'cuda'
                results['device_used'] = 'gpu'
            
            # Initialize model
            model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            
            # Test with sample texts
            test_texts = [
                "Agent Exo-Suit V4.0 GPU acceleration test",
                "Machine learning and neural networks",
                "GPU computing and CUDA programming",
                "High-performance computing and optimization"
            ]
            
            # Generate embeddings
            start_time = time.time()
            embeddings = model.encode(test_texts, show_progress_bar=False, device=device)
            end_time = time.time()
            
            results['processing_time'] = end_time - start_time
            results['embedding_count'] = embeddings.shape[0]
            results['embedding_dimension'] = embeddings.shape[1]
            results['status'] = 'OK'
            
            logger.info(f"Generated {results['embedding_count']} embeddings in {results['processing_time']:.3f}s")
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"GPU embedding test failed: {e}")
        
        return results
    
    def test_faiss_index(self) -> Dict[str, Any]:
        """Test FAISS index creation and search"""
        logger.info("Testing FAISS index...")
        
        results = {
            'status': 'FAILED',
            'index_type': 'unknown',
            'vector_count': 0,
            'search_time': 0,
            'error': None
        }
        
        try:
            import faiss
            import numpy as np
            
            # Create test embeddings
            dimension = 384  # all-MiniLM-L6-v2 dimension
            num_vectors = 100
            
            # Generate random test vectors
            test_vectors = np.random.randn(num_vectors, dimension).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(test_vectors)
            
            # Create index
            index = faiss.IndexFlatIP(dimension)
            index.add(test_vectors)
            
            results['index_type'] = type(index).__name__
            results['vector_count'] = index.ntotal
            
            # Test search
            query_vector = np.random.randn(1, dimension).astype('float32')
            faiss.normalize_L2(query_vector)
            
            start_time = time.time()
            scores, indices = index.search(query_vector, 5)
            end_time = time.time()
            
            results['search_time'] = end_time - start_time
            results['status'] = 'OK'
            
            logger.info(f"FAISS index test successful: {results['vector_count']} vectors")
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"FAISS index test failed: {e}")
        
        return results
    
    def test_file_processing(self) -> Dict[str, Any]:
        """Test file processing capabilities"""
        logger.info("Testing file processing...")
        
        results = {
            'status': 'FAILED',
            'files_processed': 0,
            'total_chunks': 0,
            'processing_time': 0,
            'error': None
        }
        
        try:
            # Get test files
            folder_test = self.test_folder_structure()
            if not folder_test['supported_files']:
                raise ValueError("No supported files found for processing")
            
            # Process first few files
            test_files = folder_test['supported_files'][:5]  # Test with 5 files
            chunks = []
            
            start_time = time.time()
            
            for file_info in test_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple chunking
                    words = content.split()
                    for i in range(0, len(words), self.test_config['chunk_size']):
                        chunk = ' '.join(words[i:i + self.test_config['chunk_size']])
                        if len(chunk.strip()) > 50:  # Minimum chunk size
                            chunks.append({
                                'file': file_info['path'],
                                'chunk_id': len(chunks),
                                'content': chunk[:200] + '...' if len(chunk) > 200 else chunk
                            })
                    
                    results['files_processed'] += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process {file_info['path']}: {e}")
                    continue
            
            end_time = time.time()
            
            results['total_chunks'] = len(chunks)
            results['processing_time'] = end_time - start_time
            results['status'] = 'OK'
            
            logger.info(f"Processed {results['files_processed']} files into {results['total_chunks']} chunks")
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"File processing test failed: {e}")
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        logger.info("Starting comprehensive V4.0 system test...")
        
        test_results = {
            'test_info': {
                'version': '4.0',
                'test_folder': self.test_folder,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_duration': 0
            },
            'system_requirements': {},
            'folder_structure': {},
            'gpu_embeddings': {},
            'faiss_index': {},
            'file_processing': {},
            'overall_status': 'FAILED',
            'summary': {}
        }
        
        # Run all tests
        test_results['system_requirements'] = self.test_system_requirements()
        test_results['folder_structure'] = self.test_folder_structure()
        test_results['gpu_embeddings'] = self.test_gpu_embeddings()
        test_results['faiss_index'] = self.test_faiss_index()
        test_results['file_processing'] = self.test_file_processing()
        
        # Calculate overall status
        all_tests = [
            test_results['system_requirements'],
            test_results['folder_structure'],
            test_results['gpu_embeddings'],
            test_results['faiss_index'],
            test_results['file_processing']
        ]
        
        passed_tests = sum(1 for test in all_tests if test.get('status') == 'OK' or test.get('folder_exists') or test.get('gpu_available'))
        total_tests = len(all_tests)
        
        test_results['overall_status'] = 'OK' if passed_tests >= total_tests * 0.8 else 'FAILED'
        test_results['test_info']['total_duration'] = time.time() - self.start_time
        
        # Generate summary
        test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%",
            'gpu_available': test_results['system_requirements'].get('gpu_available', False),
            'cuda_available': test_results['system_requirements'].get('cuda_available', False),
            'files_found': test_results['folder_structure'].get('file_count', 0)
        }
        
        return test_results
    
    def print_report(self, results: Dict[str, Any]):
        """Print formatted test report"""
        print("\n" + "="*80)
        print("AGENT EXO-SUIT V4.0 - COMPREHENSIVE SYSTEM TEST REPORT")
        print("="*80)
        
        # Test info
        print(f"Version: {results['test_info']['version']}")
        print(f"Test Folder: {results['test_info']['test_folder']}")
        print(f"Timestamp: {results['test_info']['timestamp']}")
        print(f"Duration: {results['test_info']['total_duration']:.2f}s")
        
        # Overall status
        print(f"\nOverall Status: {results['overall_status'].upper()}")
        print(f"Success Rate: {results['summary']['success_rate']}")
        
        # System requirements
        print(f"\nSystem Requirements:")
        reqs = results['system_requirements']
        print(f"  Python: {reqs.get('python_version', 'Unknown')}")
        print(f"  Platform: {reqs.get('platform', 'Unknown')}")
        print(f"  GPU Available: {reqs.get('gpu_available', False)}")
        print(f"  CUDA Available: {reqs.get('cuda_available', False)}")
        
        if reqs.get('gpu_available'):
            gpu_info = reqs.get('gpu_info', {})
            print(f"  GPU Device: {gpu_info.get('device_name', 'Unknown')}")
            print(f"  CUDA Version: {gpu_info.get('cuda_version', 'Unknown')}")
        
        # Dependencies
        print(f"\nDependencies:")
        for dep_name, dep_info in reqs.get('dependencies', {}).items():
            status = dep_info.get('status', 'Unknown')
            version = dep_info.get('version', '')
            print(f"  {dep_name}: {status} {version}")
        
        # Folder structure
        print(f"\nFolder Structure:")
        folder = results['folder_structure']
        print(f"  Folder Exists: {folder.get('folder_exists', False)}")
        print(f"  Supported Files: {folder.get('file_count', 0)}")
        print(f"  Total Size: {folder.get('total_size', 0)} bytes")
        
        # Test results
        print(f"\nTest Results:")
        tests = [
            ('GPU Embeddings', results['gpu_embeddings']),
            ('FAISS Index', results['faiss_index']),
            ('File Processing', results['file_processing'])
        ]
        
        for test_name, test_result in tests:
            status = test_result.get('status', 'Unknown')
            print(f"  {test_name}: {status}")
            
            if test_result.get('error'):
                print(f"    Error: {test_result['error']}")
        
        print("="*80)


def main():
    """Main test function"""
    print("Agent Exo-Suit V4.0 - Comprehensive System Test Suite")
    print("Testing GPU components with test folder...")
    
    # Initialize tester
    tester = V4SystemTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Print report
    tester.print_report(results)
    
    # Save results
    output_file = "v4_system_test_report.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nTest report saved to: {output_file}")
    except Exception as e:
        print(f"Failed to save report: {e}")
    
    # Return exit code
    return 0 if results['overall_status'] == 'OK' else 1


if __name__ == '__main__':
    sys.exit(main())
