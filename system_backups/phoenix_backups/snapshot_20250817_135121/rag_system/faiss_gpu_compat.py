#!/usr/bin/env python3
"""
Agent Exo-Suit V5.0 - FAISS GPU Compatibility Layer
Handles missing GPU FAISS features gracefully with fallbacks
"""

import faiss
import logging

logger = logging.getLogger(__name__)

class FAISSGPUCompat:
    """FAISS GPU compatibility layer with graceful fallbacks"""
    
    @staticmethod
    def has_gpu_resources():
        """Check if GPU resources are available"""
        return hasattr(faiss, 'StandardGpuResources')
    
    @staticmethod
    def has_gpu_index_types():
        """Check if GPU index types are available"""
        return hasattr(faiss, 'GpuIndexIVFFlat')
    
    @staticmethod
    def create_gpu_resources():
        """Create GPU resources with fallback"""
        if FAISSGPUCompat.has_gpu_resources():
            try:
                return faiss.StandardGpuResources()
            except Exception as e:
                logger.warning(f"Failed to create GPU resources: {e}")
                return None
        else:
            logger.warning("GPU resources not available in this FAISS version")
            return None
    
    @staticmethod
    def index_cpu_to_gpu(resources, gpu_id, index):
        """Convert CPU index to GPU with fallback"""
        if resources is None:
            logger.warning("No GPU resources available, returning CPU index")
            return index
        
        if hasattr(faiss, 'index_cpu_to_gpu'):
            try:
                return faiss.index_cpu_to_gpu(resources, gpu_id, index)
            except Exception as e:
                logger.warning(f"GPU index conversion failed: {e}, using CPU index")
                return index
        else:
            logger.warning("GPU index conversion not available, using CPU index")
            return index
    
    @staticmethod
    def index_gpu_to_cpu(gpu_index):
        """Convert GPU index back to CPU with fallback"""
        if hasattr(faiss, 'index_gpu_to_cpu'):
            try:
                return faiss.index_gpu_to_cpu(gpu_index)
            except Exception as e:
                logger.warning(f"GPU to CPU index conversion failed: {e}")
                return gpu_index
        else:
            logger.warning("GPU to CPU index conversion not available")
            return gpu_index
    
    @staticmethod
    def get_gpu_info():
        """Get GPU information with fallback"""
        gpu_info = {
            'available': False,
            'count': 0,
            'features': {
                'resources': FAISSGPUCompat.has_gpu_resources(),
                'index_types': FAISSGPUCompat.has_gpu_index_types(),
                'conversion': hasattr(faiss, 'index_cpu_to_gpu'),
                'profiling': hasattr(faiss, 'gpu_profiler_start'),
                'knn': hasattr(faiss, 'knn_gpu')
            }
        }
        
        try:
            gpu_info['count'] = faiss.get_num_gpus()
            gpu_info['available'] = gpu_info['count'] > 0
        except Exception as e:
            logger.warning(f"Could not get GPU count: {e}")
        
        return gpu_info

# Global compatibility instance
faiss_gpu = FAISSGPUCompat()
