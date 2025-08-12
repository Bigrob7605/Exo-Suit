#!/usr/bin/env python3
"""
Agent Exo-Suit V5.0 "Builder of Dreams" - Full Project Scanner
Uses the hybrid RAG system to efficiently scan the entire project
"""

import sys
import time
import psutil
import torch
from pathlib import Path
from hybrid_rag_v4 import HybridRAGProcessor

def scan_full_project():
    """Scan the entire project using V5.0 hybrid RAG system"""
    print("🚀 AGENT EXO-SUIT V5.0 'BUILDER OF DREAMS' - FULL PROJECT SCANNER")
    print("=" * 80)
    
    start_time = time.time()
    
    # Configuration for maximum performance
    config = {
        'model_name': 'all-MiniLM-L6-v2',
        'batch_size': 1000,  # Large batch size for efficiency
        'num_workers': 8,    # More workers for parallel processing
        'ram_disk_size_gb': 4,
        'gpu_memory_threshold': 0.9  # Use more GPU memory
    }
    
    try:
        print("Initializing V5.0 Hybrid RAG System...")
        processor = HybridRAGProcessor(config)
        
        # Get project root
        project_root = Path("..")
        print(f"Project root: {project_root.absolute()}")
        
        # Define file extensions to scan
        extensions = [
            '*.py', '*.ps1', '*.md', '*.txt', '*.json', '*.yaml', '*.yml',
            '*.js', '*.ts', '*.html', '*.css', '*.xml', '*.csv', '*.log'
        ]
        
        print("Scanning project files...")
        project_files = []
        for ext in extensions:
            files = list(project_root.rglob(ext))
            project_files.extend(files)
            print(f"  {ext}: {len(files)} files")
        
        # Filter files by size (skip very large files)
        print("\nFiltering files by size...")
        filtered_files = []
        total_size = 0
        for file_path in project_files:
            try:
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    # Skip files larger than 10MB
                    if file_size < 10 * 1024 * 1024:
                        filtered_files.append(str(file_path))
                        total_size += file_size
            except:
                continue
        
        print(f"Total files found: {len(project_files)}")
        print(f"Files to process: {len(filtered_files)}")
        print(f"Total size: {total_size / (1024**3):.2f} GB")
        
        # Process files in batches
        print(f"\nProcessing files with batch size: {config['batch_size']}")
        print("GPU acceleration: ENABLED")
        print("Hybrid processing: ENABLED")
        
        batch_start = time.time()
        results = processor.process_files(filtered_files, batch_size=config['batch_size'])
        batch_time = time.time() - batch_start
        
        # Calculate performance metrics
        files_per_second = len(filtered_files) / batch_time
        total_time = time.time() - start_time
        
        print(f"\n=== SCANNING COMPLETED ===")
        print(f"Files processed: {len(filtered_files)}")
        print(f"Processing time: {batch_time:.2f} seconds")
        print(f"Speed: {files_per_second:.1f} files/second")
        print(f"Total time: {total_time:.2f} seconds")
        
        # Build search index
        print("\nBuilding search index...")
        if processor.build_index(results):
            print("✅ Search index built successfully!")
            
            # Test search functionality
            test_queries = [
                "GPU acceleration",
                "AI agent development",
                "security scanning",
                "performance optimization"
            ]
            
            print("\nTesting search functionality:")
            for query in test_queries:
                search_results = processor.search(query, top_k=3)
                print(f"  '{query}': {len(search_results)} results")
        
        # Performance statistics
        stats = processor.get_performance_stats()
        print(f"\nPerformance Statistics:")
        print(f"  Files processed: {stats.get('total_files_processed', 0)}")
        print(f"  Successful: {stats.get('successful_processing', 0)}")
        print(f"  Failed: {stats.get('failed_processing', 0)}")
        print(f"  Avg time: {stats.get('average_processing_time', 0):.3f}s")
        
        # Memory usage
        system_memory = psutil.virtual_memory()
        print(f"\nMemory Usage:")
        print(f"  System RAM: {system_memory.used / (1024**3):.1f} GB / {system_memory.total / (1024**3):.1f} GB")
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0)
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            total = gpu_memory.total_memory / (1024**3)
            print(f"  GPU VRAM: {allocated:.1f} GB / {total:.1f} GB")
        
        # Cleanup
        print("\nCleaning up...")
        processor.cleanup()
        
        print(f"\n🎯 V5.0 FULL PROJECT SCAN COMPLETED SUCCESSFULLY!")
        print(f"Performance: {files_per_second:.1f} files/second")
        print(f"Efficiency: {len(filtered_files) / total_time:.1f} files/second overall")
        
        return True
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = scan_full_project()
    sys.exit(0 if success else 1)
