#!/usr/bin/env python3
"""
Agent Exo-Suit V3.0 - RAG Retrieval Engine
Robust retrieval with CPU/GPU support and comprehensive error handling
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
try:
    from device_manager import DeviceManager
    from embedding_engine import EmbeddingEngine
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all required modules are in the same directory")
    sys.exit(1)

# Import FAISS with fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError as e:
    print(f"FAISS not available: {e}")
    print("Please install FAISS for retrieval functionality")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGRetriever:
    """Advanced RAG retrieval engine with device management and error handling"""
    
    def __init__(self, index_dir: str, config: Optional[Dict[str, Any]] = None):
        self.index_dir = index_dir
        self.config = config or {}
        
        # Initialize components
        self.device_manager = None
        self.embedding_engine = None
        
        # Loaded data
        self.index = None
        self.metadata = []
        self.chunks = []
        
        # Performance tracking
        self.retrieval_stats = {
            'total_queries': 0,
            'total_time': 0.0,
            'avg_time_per_query': 0.0,
            'device_used': None
        }
        
        # Initialize the system
        self._initialize_system()
        self._load_index()
    
    def _initialize_system(self):
        """Initialize system components"""
        logger.info("Initializing RAG Retriever V3.0...")
        
        try:
            # Initialize device manager
            logger.info("Initializing device manager...")
            self.device_manager = DeviceManager(self.config)
            
            # Print system capabilities
            self.device_manager.print_system_summary()
            
            # Get optimal configuration
            device_config = self.device_manager.get_optimal_configuration()
            logger.info(f"Using device configuration: {device_config['mode']}")
            
            # Initialize embedding engine
            logger.info("Initializing embedding engine...")
            self.embedding_engine = EmbeddingEngine(
                model_name=self.config.get('model_name', 'all-MiniLM-L6-v2'),
                device_mode=device_config['mode'],
                batch_size=device_config.get('batch_size', 32),
                fallback_strategy=device_config.get('fallback_strategy', 'cpu_fallback')
            )
            
            logger.info("System initialization completed successfully")
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            raise
    
    def _load_index(self):
        """Load FAISS index and metadata"""
        logger.info("Loading RAG index...")
        
        try:
            # Load FAISS index
            index_path = os.path.join(self.index_dir, "index.faiss")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index file not found: {index_path}")
            
            self.index = faiss.read_index(index_path)
            logger.info(f"FAISS index loaded: {self.index.ntotal} vectors")
            
            # Load metadata
            metadata_path = os.path.join(self.index_dir, "meta.jsonl")
            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
            
            self.metadata = []
            self.chunks = []
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        chunk_data = json.loads(line.strip())
                        self.metadata.append(chunk_data)
                        self.chunks.append(chunk_data['chunk_text'])
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
                        continue
            
            logger.info(f"Metadata loaded: {len(self.metadata)} chunks")
            
            # Validate index and metadata consistency
            if len(self.metadata) != self.index.ntotal:
                logger.warning(f"Index-metadata mismatch: {self.index.ntotal} vectors vs {len(self.metadata)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, 
               similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if not query or not query.strip():
            return []
        
        start_time = time.time()
        
        try:
            logger.info(f"Searching for: '{query}' (top_k={top_k})")
            
            # Generate query embedding
            query_embedding = self.embedding_engine.generate_embeddings([query])
            
            if query_embedding.size == 0:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search index
            query_vector = query_embedding.astype('float32')
            
            # Perform search
            if hasattr(self.index, 'search'):
                # Standard FAISS search
                similarities, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            else:
                # Fallback for non-standard indices
                logger.warning("Using fallback search method")
                similarities, indices = self._fallback_search(query_vector, top_k)
            
            # Process results
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                
                if similarity < similarity_threshold:
                    continue
                
                # Get chunk data
                chunk_data = self.metadata[idx].copy()
                chunk_data['similarity_score'] = float(similarity)
                chunk_data['rank'] = i + 1
                
                results.append(chunk_data)
            
            # Update statistics
            query_time = time.time() - start_time
            self.retrieval_stats['total_queries'] += 1
            self.retrieval_stats['total_time'] += query_time
            self.retrieval_stats['avg_time_per_query'] = (
                self.retrieval_stats['total_time'] / self.retrieval_stats['total_queries']
            )
            self.retrieval_stats['device_used'] = self.embedding_engine.device_type
            
            logger.info(f"Search completed in {query_time:.3f}s: {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _fallback_search(self, query_vector: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Fallback search method for non-standard FAISS indices"""
        try:
            # Convert query vector to 1D if needed
            if query_vector.ndim > 1:
                query_vector = query_vector.flatten()
            
            # Get all vectors from index (this is inefficient but works as fallback)
            all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
            
            # Calculate similarities manually
            similarities = np.dot(all_vectors, query_vector)
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            top_similarities = similarities[top_indices]
            
            return top_similarities.reshape(1, -1), top_indices.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            # Return empty results
            return np.array([[]]), np.array([[]])
    
    def batch_search(self, queries: List[str], top_k: int = 5,
                    similarity_threshold: float = 0.0) -> List[List[Dict[str, Any]]]:
        """Search for multiple queries at once"""
        if not queries:
            return []
        
        logger.info(f"Batch searching {len(queries)} queries...")
        
        all_results = []
        
        for i, query in enumerate(queries):
            try:
                results = self.search(query, top_k, similarity_threshold)
                all_results.append(results)
                
                logger.debug(f"Query {i+1}/{len(queries)}: {len(results)} results")
                
            except Exception as e:
                logger.error(f"Query {i+1} failed: {e}")
                all_results.append([])
        
        logger.info(f"Batch search completed: {len(all_results)} queries processed")
        return all_results
    
    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by its index"""
        if 0 <= chunk_id < len(self.metadata):
            return self.metadata[chunk_id].copy()
        return None
    
    def get_chunks_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all chunks from a specific file"""
        file_chunks = []
        
        for chunk_data in self.metadata:
            if chunk_data.get('file_path') == file_path:
                file_chunks.append(chunk_data.copy())
        
        return file_chunks
    
    def get_file_summary(self) -> Dict[str, Any]:
        """Get summary of indexed files"""
        file_stats = {}
        
        for chunk_data in self.metadata:
            file_path = chunk_data.get('file_path', 'unknown')
            
            if file_path not in file_stats:
                file_stats[file_path] = {
                    'file_type': chunk_data.get('file_type', 'unknown'),
                    'file_extension': chunk_data.get('file_extension', 'unknown'),
                    'total_chunks': 0,
                    'total_size': 0,
                    'chunk_sizes': []
                }
            
            file_stats[file_path]['total_chunks'] += 1
            file_stats[file_path]['total_size'] += chunk_data.get('chunk_size', 0)
            file_stats[file_path]['chunk_sizes'].append(chunk_data.get('chunk_size', 0))
        
        # Calculate averages
        for file_info in file_stats.values():
            if file_info['chunk_sizes']:
                file_info['avg_chunk_size'] = sum(file_info['chunk_sizes']) / len(file_info['chunk_sizes'])
                file_info['min_chunk_size'] = min(file_info['chunk_sizes'])
                file_info['max_chunk_size'] = max(file_info['chunk_sizes'])
        
        return file_stats
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        stats = {
            'index_info': {
                'total_vectors': self.index.ntotal if self.index else 0,
                'vector_dimension': self.index.d if self.index else 0,
                'index_type': type(self.index).__name__ if self.index else 'None'
            },
            'metadata_info': {
                'total_chunks': len(self.metadata),
                'total_files': len(set(chunk.get('file_path') for chunk in self.metadata)),
                'file_types': {},
                'extensions': {}
            },
            'retrieval_stats': self.retrieval_stats.copy(),
            'system_info': {
                'device_used': self.embedding_engine.device_type if self.embedding_engine else 'Unknown',
                'model_used': self.embedding_engine.model_name if self.embedding_engine else 'Unknown'
            }
        }
        
        # Calculate file type and extension statistics
        for chunk in self.metadata:
            file_type = chunk.get('file_type', 'unknown')
            stats['metadata_info']['file_types'][file_type] = stats['metadata_info']['file_types'].get(file_type, 0) + 1
            
            ext = chunk.get('file_extension', 'unknown')
            stats['metadata_info']['extensions'][ext] = stats['metadata_info']['extensions'].get(ext, 0) + 1
        
        return stats
    
    def print_index_summary(self):
        """Print a summary of the loaded index"""
        stats = self.get_index_stats()
        
        print("\n" + "="*60)
        print("AGENT EXO-SUIT V3.0 - RAG INDEX SUMMARY")
        print("="*60)
        print(f"Index vectors: {stats['index_info']['total_vectors']}")
        print(f"Vector dimension: {stats['index_info']['vector_dimension']}")
        print(f"Total chunks: {stats['metadata_info']['total_chunks']}")
        print(f"Total files: {stats['metadata_info']['total_files']}")
        print(f"Device: {stats['system_info']['device_used']}")
        print(f"Model: {stats['system_info']['model_used']}")
        
        print(f"\nFile types:")
        for file_type, count in sorted(stats['metadata_info']['file_types'].items()):
            print(f"  {file_type}: {count}")
        
        print(f"\nTop extensions:")
        for ext, count in sorted(stats['metadata_info']['extensions'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ext}: {count}")
        
        print("="*60)


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='RAG retrieval with CPU/GPU support')
    parser.add_argument('--index-dir', required=True,
                       help='Directory containing the RAG index')
    parser.add_argument('--query', required=True,
                       help='Search query')
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of top results to return')
    parser.add_argument('--threshold', type=float, default=0.0,
                       help='Similarity threshold for results')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                       help='Sentence transformer model to use')
    parser.add_argument('--device', choices=['auto', 'cpu', 'gpu', 'hybrid'], default='auto',
                       help='Device mode for processing')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for embedding generation')
    parser.add_argument('--summary', action='store_true',
                       help='Print index summary instead of searching')
    
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = {
            'model_name': args.model,
            'device_mode': args.device,
            'batch_size': args.batch_size
        }
        
        # Create retriever
        retriever = RAGRetriever(args.index_dir, config)
        
        if args.summary:
            # Print index summary
            retriever.print_index_summary()
        else:
            # Perform search
            results = retriever.search(args.query, args.top_k, args.threshold)
            
            if results:
                print(f"\n Search results for: '{args.query}'")
                print(f"Found {len(results)} results:")
                
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Score: {result['similarity_score']:.4f}")
                    print(f"   File: {result['file_path']}")
                    print(f"   Type: {result['file_type']}")
                    print(f"   Chunk: {result['chunk_index'] + 1}/{result['total_chunks']}")
                    print(f"   Text: {result['chunk_text'][:200]}...")
            else:
                print(f"\n No results found for: '{args.query}'")
        
        return 0
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        print(f"\n Retrieval failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
