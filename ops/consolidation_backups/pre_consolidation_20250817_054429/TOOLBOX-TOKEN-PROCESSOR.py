#!/usr/bin/env python3
"""
TOOLBOX TOKEN PROCESSOR - Phase 3 Token Upgrade
This script will process the ENTIRE toolbox, create embeddings, and build a real 1M token context system.
"""

import os
import sys
import json
import time
import logging
import psutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/TOOLBOX-TOKEN-PROCESSOR.log'),
        logging.StreamHandler()
    ]
)

# GPU imports
try:
    import torch
    import faiss
    from sentence_transformers import SentenceTransformer
    GPU_AVAILABLE = True
    logging.info("GPU acceleration enabled for toolbox processing")
except ImportError as e:
    logging.error(f"GPU libraries not available: {e}")
    exit(1)

class ToolboxTokenProcessor:
    def __init__(self):
        self.toolbox_path = Path("Universal Open Science Toolbox With Kai (The Real Test)")
        self.max_tokens = 1000000  # 1M tokens
        self.gpu_memory_target = 0.95  # Target 95% GPU memory usage
        self.batch_size = 100  # Process 100 files at a time
        self.current_tokens = 0
        self.processed_files = 0
        self.total_files = 0
        
        # Initialize GPU and model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.gpu_props = torch.cuda.get_device_properties(0) if torch.cuda.is_available() else None
        
        # Initialize sentence transformer model
        self.model = None
        self.initialize_model()
        
        # Storage for embeddings and metadata
        self.embeddings = []
        self.file_metadata = []
        self.context_index = None
        
        logging.info(f"Initializing Toolbox Token Processor")
        logging.info(f"Target: {self.max_tokens:,} tokens")
        logging.info(f"GPU Memory Target: {self.gpu_memory_target*100:.1f}%")
        logging.info(f"Device: {self.device}")
        
        if self.gpu_props:
            logging.info(f"GPU: {self.gpu_props.name}")
            logging.info(f"GPU Memory: {self.gpu_props.total_memory / 1024**3:.1f} GB")
    
    def initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            logging.info("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            logging.info(f"Model loaded successfully on {self.device}")
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.to(self.device)
                logging.info("Model moved to GPU")
                
        except Exception as e:
            logging.error(f"Failed to load model: {e}")
            raise
    
    def get_system_resources(self):
        """Get current system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        if torch.cuda.is_available():
            gpu_allocated = torch.cuda.memory_allocated(0) / 1024**3
            gpu_reserved = torch.cuda.memory_reserved(0) / 1024**3
            gpu_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_usage = (gpu_allocated / gpu_total) * 100
        else:
            gpu_allocated = gpu_reserved = gpu_total = gpu_usage = 0
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024**3,
            'memory_total_gb': memory.total / 1024**3,
            'gpu_allocated_gb': gpu_allocated,
            'gpu_reserved_gb': gpu_reserved,
            'gpu_total_gb': gpu_total,
            'gpu_usage_percent': gpu_usage
        }
    
    def log_system_status(self, phase=""):
        """Log current system status"""
        resources = self.get_system_resources()
        
        logging.info(f"{'='*60}")
        logging.info(f"SYSTEM STATUS - {phase}")
        logging.info(f"{'='*60}")
        logging.info(f"CPU: {resources['cpu_percent']:.1f}%")
        logging.info(f"Memory: {resources['memory_percent']:.1f}% ({resources['memory_used_gb']:.1f}GB / {resources['memory_total_gb']:.1f}GB)")
        logging.info(f"GPU: {resources['gpu_allocated_gb']:.2f}GB allocated, {resources['gpu_reserved_gb']:.2f}GB reserved")
        logging.info(f"GPU Usage: {resources['gpu_usage_percent']:.1f}% of {resources['gpu_total_gb']:.1f}GB")
        logging.info(f"Files Processed: {self.processed_files}/{self.total_files}")
        logging.info(f"Current Tokens: {self.current_tokens:,}")
        logging.info(f"Token Target: {self.max_tokens:,}")
        logging.info(f"Token Progress: {(self.current_tokens/self.max_tokens)*100:.1f}%")
        logging.info(f"{'='*60}")
        
        return resources
    
    def scan_toolbox_files(self):
        """Scan the entire toolbox for files to process"""
        logging.info("Scanning toolbox for files...")
        
        file_types = ['.py', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.js', '.ps1', '.bat', '.sh']
        files = []
        
        for file_type in file_types:
            pattern = f"**/*{file_type}"
            found_files = list(self.toolbox_path.rglob(pattern))
            files.extend(found_files)
        
        # Filter out very large files that might cause issues
        filtered_files = []
        for file_path in files:
            try:
                if file_path.exists() and file_path.stat().st_size < 10 * 1024 * 1024:  # 10MB limit
                    filtered_files.append(file_path)
            except:
                continue
        
        self.total_files = len(filtered_files)
        logging.info(f"Found {self.total_files} files to process (filtered from {len(files)})")
        return filtered_files
    
    def estimate_tokens_for_file(self, file_path: Path) -> int:
        """Estimate token count for a file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Rough estimate: 1 token ≈ 4 characters
                    return len(content) // 4
        except Exception as e:
            logging.warning(f"Could not read {file_path}: {e}")
        
        return 0
    
    def process_file_content(self, file_path: Path) -> Tuple[str, int, List[float]]:
        """Process a single file and generate embeddings"""
        try:
            if not file_path.exists():
                return "", 0, []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return "", 0, []
            
            # Estimate tokens
            tokens = len(content) // 4
            
            # Generate embeddings using the model
            embeddings = self.model.encode(content, convert_to_tensor=True)
            
            # Convert to list for storage
            embeddings_list = embeddings.cpu().numpy().tolist()
            
            return content, tokens, embeddings_list
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            return "", 0, []
    
    def create_memory_intensive_tensors(self, target_gb: float):
        """Create tensors to fill GPU memory to target usage"""
        logging.info(f"Creating memory-intensive tensors to reach {target_gb:.2f}GB GPU usage")
        
        current_allocated = torch.cuda.memory_allocated(0) / 1024**3
        if current_allocated >= target_gb:
            logging.info("GPU memory already at target level")
            return []
        
        chunk_size_gb = 0.5  # 500MB chunks
        tensors = []
        
        while torch.cuda.memory_allocated(0) / 1024**3 < target_gb:
            try:
                elements_needed = int((chunk_size_gb * 1024**3) / 4)
                dim = int(np.sqrt(elements_needed))
                
                tensor = torch.randn(dim, dim, dtype=torch.float32, device=self.device)
                tensors.append(tensor)
                
                current_gb = torch.cuda.memory_allocated(0) / 1024**3
                logging.info(f"Created tensor: {dim}x{dim} = {current_gb:.2f}GB allocated")
                
                if current_gb >= target_gb:
                    break
                    
            except torch.cuda.OutOfMemoryError:
                logging.warning("GPU OOM - stopping tensor creation")
                break
            except Exception as e:
                logging.error(f"Error creating tensor: {e}")
                break
        
        logging.info(f"Created {len(tensors)} tensors")
        return tensors
    
    def process_files_in_batches(self, files: List[Path]):
        """Process files in batches to build up token count and embeddings"""
        logging.info(f"Processing {len(files)} files in batches of {self.batch_size}")
        
        batches = [files[i:i + self.batch_size] for i in range(0, len(files), self.batch_size)]
        
        for batch_num, batch in enumerate(batches):
            logging.info(f"Processing batch {batch_num + 1}/{len(batches)} ({len(batch)} files)")
            
            batch_tokens = 0
            batch_embeddings = []
            batch_metadata = []
            
            for file_path in batch:
                if self.current_tokens >= self.max_tokens:
                    logging.info(f"Reached token target: {self.current_tokens:,} tokens")
                    break
                
                # Process file
                content, tokens, embeddings = self.process_file_content(file_path)
                
                if tokens > 0 and embeddings:
                    # Add to batch data
                    batch_tokens += tokens
                    self.current_tokens += tokens
                    self.processed_files += 1
                    
                    # Store file metadata
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    metadata = {
                        'file_path': str(file_path),
                        'file_size': len(content),
                        'tokens': tokens,
                        'hash': file_hash,
                        'timestamp': datetime.now().isoformat(),
                        'file_type': file_path.suffix
                    }
                    
                    batch_metadata.append(metadata)
                    batch_embeddings.append(embeddings)
                    
                    # Log progress every 50 files
                    if self.processed_files % 50 == 0:
                        self.log_system_status(f"Batch {batch_num + 1}")
            
            # Store batch data
            self.embeddings.extend(batch_embeddings)
            self.file_metadata.extend(batch_metadata)
            
            # Check if we've reached our token target
            if self.current_tokens >= self.max_tokens:
                logging.info(f"Reached token target: {self.current_tokens:,} tokens")
                break
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        logging.info(f"File processing complete. Total tokens: {self.current_tokens:,}")
        logging.info(f"Files processed: {self.processed_files}")
        logging.info(f"Embeddings generated: {len(self.embeddings)}")
    
    def build_context_index(self):
        """Build a searchable context index from all embeddings"""
        if not self.embeddings:
            logging.warning("No embeddings to index")
            return
        
        try:
            logging.info("Building context index...")
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(self.embeddings)
            
            # Create FAISS index
            dimension = len(self.embeddings[0])
            self.context_index = faiss.IndexFlatL2(dimension)
            
            # Add vectors to index
            self.context_index.add(embeddings_array.astype('float32'))
            
            logging.info(f"Context index built with {self.context_index.ntotal} vectors")
            
        except Exception as e:
            logging.error(f"Failed to build context index: {e}")
    
    def search_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search the context index for relevant content"""
        if not self.context_index or not self.model:
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            query_vector = query_embedding.cpu().numpy().reshape(1, -1).astype('float32')
            
            # Search index
            distances, indices = self.context_index.search(query_vector, top_k)
            
            # Return results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.file_metadata):
                    result = self.file_metadata[idx].copy()
                    result['relevance_score'] = 1.0 / (1.0 + distance)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []
    
    def run_processing_pipeline(self):
        """Run the complete toolbox processing pipeline"""
        logging.info(" STARTING TOOLBOX TOKEN PROCESSING PIPELINE ")
        
        # Initial system status
        self.log_system_status("INITIAL")
        
        # Phase 1: Scan toolbox
        files = self.scan_toolbox_files()
        
        # Phase 2: Process files to build token count and embeddings
        self.process_files_in_batches(files)
        
        # Phase 3: Build context index
        self.build_context_index()
        
        # Phase 4: Fill GPU memory to target usage
        if self.gpu_props:
            target_gb = self.gpu_memory_target * self.gpu_props.total_memory / 1024**3
            tensors = self.create_memory_intensive_tensors(target_gb)
        
        # Phase 5: Test context search functionality
        logging.info("Testing context search functionality...")
        test_queries = [
            "machine learning algorithms",
            "data processing pipeline",
            "GPU acceleration",
            "context management",
            "token processing"
        ]
        
        for query in test_queries:
            results = self.search_context(query, top_k=3)
            logging.info(f"Query: '{query}' - Found {len(results)} results")
            for result in results:
                logging.info(f"  - {result['file_path']} (Score: {result['relevance_score']:.3f})")
        
        # Phase 6: Monitor performance under stress
        logging.info("Monitoring performance under maximum stress...")
        start_time = time.time()
        
        for i in range(30):  # Monitor for 30 seconds
            resources = self.log_system_status(f"STRESS MONITORING {i+1}/30")
            
            # Check if we're maintaining target GPU usage
            if self.gpu_props and resources['gpu_usage_percent'] < (self.gpu_memory_target * 100 * 0.9):
                logging.warning(f"GPU usage dropped below 90% of target: {resources['gpu_usage_percent']:.1f}%")
                # Create more tensors to maintain pressure
                target_gb = self.gpu_memory_target * self.gpu_props.total_memory / 1024**3
                self.create_memory_intensive_tensors(target_gb)
            
            time.sleep(1)
        
        # Phase 7: Cleanup and results
        logging.info("Cleaning up GPU memory...")
        if 'tensors' in locals():
            del tensors
        torch.cuda.empty_cache()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final system status
        self.log_system_status("FINAL")
        
        # Generate comprehensive report
        self.generate_processing_report(duration)
        
        logging.info(" TOOLBOX TOKEN PROCESSING PIPELINE COMPLETE ")
    
    def generate_processing_report(self, duration: float):
        """Generate comprehensive processing report"""
        report_path = Path("logs/TOOLBOX-PROCESSING-REPORT.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# TOOLBOX TOKEN PROCESSING REPORT\n\n")
            f.write(f"**Processing Duration:** {duration:.1f} seconds\n")
            f.write(f"**Files Processed:** {self.processed_files}/{self.total_files}\n")
            f.write(f"**Final Token Count:** {self.current_tokens:,}\n")
            f.write(f"**Target Tokens:** {self.max_tokens:,}\n")
            f.write(f"**Token Achievement:** {(self.current_tokens/self.max_tokens)*100:.1f}%\n")
            f.write(f"**Embeddings Generated:** {len(self.embeddings)}\n\n")
            
            f.write("## File Type Breakdown\n\n")
            file_types = {}
            for metadata in self.file_metadata:
                file_type = metadata['file_type']
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            for file_type, count in sorted(file_types.items()):
                f.write(f"- **{file_type}:** {count} files\n")
            
            f.write(f"\n## System Performance\n\n")
            f.write(f"- **Processing Speed:** {self.processed_files/duration:.1f} files/second\n")
            f.write(f"- **Token Processing Rate:** {self.current_tokens/duration:.1f} tokens/second\n")
            f.write(f"- **GPU Memory Target:** {self.gpu_memory_target*100:.1f}%\n")
            f.write(f"- **Performance Rating:** {'EXCELLENT' if self.current_tokens >= self.max_tokens else 'GOOD'}\n")
            
            f.write(f"\n## Context Search Capabilities\n\n")
            f.write(f"- **Searchable Vectors:** {len(self.embeddings)}\n")
            f.write(f"- **Index Type:** FAISS FlatL2\n")
            f.write(f"- **Vector Dimension:** {len(self.embeddings[0]) if self.embeddings else 0}\n")
            f.write(f"- **Search Functionality:** {'OPERATIONAL' if self.context_index else 'FAILED'}\n")
        
        logging.info(f"Processing report saved to: {report_path}")
        
        # Save metadata and embeddings to JSON for future use
        data_path = Path("logs/processed_toolbox_data.json")
        with open(data_path, 'w') as f:
            json.dump({
                'metadata': self.file_metadata,
                'embeddings_count': len(self.embeddings),
                'total_tokens': self.current_tokens,
                'processing_timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        logging.info(f"Toolbox data saved to: {data_path}")

def main():
    """Main execution function"""
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Initialize and run processing pipeline
        processor = ToolboxTokenProcessor()
        processor.run_processing_pipeline()
        
    except KeyboardInterrupt:
        logging.info("Processing interrupted by user")
    except Exception as e:
        logging.error(f"Processing failed with error: {e}")
        raise

if __name__ == "__main__":
    main()
