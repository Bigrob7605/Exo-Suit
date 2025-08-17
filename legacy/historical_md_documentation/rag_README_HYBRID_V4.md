# Agent Exo-Suit V4.0 - Enhanced Hybrid CPU+GPU RAG System

##  **OVERVIEW**

The Enhanced Hybrid CPU+GPU RAG System represents the pinnacle of performance optimization, combining the best of both CPU and GPU processing with advanced features like RAM disk optimization, intelligent load balancing, and bottleneck elimination.

###  **Key Features**

- ** Hybrid Processing**: Seamlessly combines CPU and GPU for optimal performance
- ** RAM Disk Optimization**: High-speed in-memory file processing
- ** Intelligent Memory Management**: Automatic memory optimization and cleanup
- ** Dynamic Load Balancing**: Smart device selection based on workload and memory
- ** Fault Tolerance**: Graceful error handling and recovery
- ** Real-time Monitoring**: Performance metrics and resource tracking
- ** Bottleneck Elimination**: Optimized processing pipeline for maximum speed

##  **ARCHITECTURE**



                    HYBRID RAG V4.0 SYSTEM                  

              
     CPU Core         GPU Core        RAM Disk       
    Processing      Acceleration     Optimization    
              

              
   Intelligent        Memory           Device        
  Load Balancing    Management        Selection      
              

              
     FAISS           Sentence         Processing     
     Index         Transformers        Pipeline      
              



##  **REQUIREMENTS**

### **System Requirements**
- **OS**: Windows 10/11, Linux, macOS
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ (16GB+ for optimal performance)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: SSD recommended for faster I/O

### **Software Requirements**
- **Python**: 3.8+
- **CUDA**: 11.6+ (for GPU acceleration)
- **PyTorch**: 2.0+

##  **INSTALLATION**

### **1. Clone the Repository**
bash
git clone <repository-url>
cd agent-exo-suit-v4


### **2. Install Dependencies**
bash
# Install core requirements
pip install -r rag/requirements_hybrid_v4.txt

# For GPU acceleration (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For GPU FAISS (optional)
pip install faiss-gpu


### **3. Verify Installation**
bash
# Test basic functionality
python rag/test_hybrid_comprehensive_v4.py

# Test GPU support
python -c "import torch; print('CUDA:', torch.cuda.is_available())"


##  **QUICK START**

### **PowerShell (Windows)**
powershell
# Run comprehensive tests
.\rag\run-hybrid-rag-v4.ps1 -Mode test

# Build index from documents
.\rag\run-hybrid-rag-v4.ps1 -Mode build -InputDir ".\docs" -BatchSize 64

# Search the index
.\rag\run-hybrid-rag-v4.ps1 -Mode search -Query "machine learning" -TopK 10

# Performance benchmark
.\rag\run-hybrid-rag-v4.ps1 -Mode benchmark

# Monitor system resources
.\rag\run-hybrid-rag-v4.ps1 -Monitor


### **Python Direct**
python
from rag.hybrid_rag_v4 import HybridRAGProcessor

# Initialize processor
config = {
    'model_name': 'all-MiniLM-L6-v2',
    'batch_size': 32,
    'num_workers': 4
}

processor = HybridRAGProcessor(config)

# Process files
file_paths = ['doc1.txt', 'doc2.txt', 'doc3.txt']
results = processor.process_files(file_paths)

# Build index
processor.build_index(results)

# Search
search_results = processor.search("your query", top_k=5)

# Cleanup
processor.cleanup()


##  **CONFIGURATION**

### **Configuration File: hybrid_config_v4.yaml**

yaml
# Device Configuration
device:
  primary: "auto"  # auto, cuda, cpu
  hybrid_mode: true
  load_balancing: "dynamic"

# RAM Disk Configuration
ram_disk:
  enabled: true
  size_gb: 4
  cleanup_interval: 100

# Memory Management
memory:
  system_threshold: 0.8
  gpu_threshold: 0.85
  cleanup_aggressive: true

# Performance Optimization
performance:
  mixed_precision: true
  warmup_batches: 3
  prefetch_factor: 2


### **Environment Variables**
bash
# Set CUDA device
export CUDA_VISIBLE_DEVICES=0

# Memory optimization
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Performance tuning
export OMP_NUM_THREADS=8


##  **ADVANCED FEATURES**

### **1. RAM Disk Optimization**
- **In-Memory Processing**: Files are processed directly in RAM for maximum speed
- **Automatic Cleanup**: Memory is freed automatically after processing
- **Size Management**: Configurable RAM disk size based on available memory

### **2. Intelligent Load Balancing**
- **Memory-Aware**: Automatically selects device based on memory availability
- **Performance-Based**: Tracks processing speed and optimizes device selection
- **Dynamic Scaling**: Adjusts worker count based on system load

### **3. Memory Management**
- **Automatic Cleanup**: Proactive memory management to prevent OOM errors
- **GPU Memory Pool**: Optimized GPU memory usage with PyTorch
- **Garbage Collection**: Intelligent garbage collection timing

### **4. Fault Tolerance**
- **Error Recovery**: Continues processing even if individual files fail
- **Graceful Degradation**: Falls back to CPU if GPU becomes unavailable
- **Checkpointing**: Saves progress to resume interrupted operations

##  **PERFORMANCE MONITORING**

### **Real-time Metrics**
python
# Get performance statistics
stats = processor.get_performance_stats()
print(f"Files processed: {stats['total_files_processed']}")
print(f"Processing speed: {stats['files_per_second']:.2f} files/sec")
print(f"Memory usage: {stats['total_memory_used']:.2f} GB")


### **Resource Monitoring**
powershell
# Monitor system resources
.\rag\run-hybrid-rag-v4.ps1 -Monitor


### **Performance Reports**
- **Automatic Logging**: All operations are logged with timestamps
- **Performance Metrics**: Processing speed, memory usage, device utilization
- **JSON Reports**: Structured performance data for analysis

##  **TESTING**

### **Comprehensive Test Suite**
bash
# Run all tests
python rag/test_hybrid_comprehensive_v4.py

# Individual test components
python -c "
from rag.test_hybrid_comprehensive_v4 import *
test_memory_management()
test_ram_disk()
test_hybrid_processor_basic()
"


### **Test Coverage**
-  Memory Management
-  RAM Disk Operations
-  Hybrid Processing
-  Device Selection
-  Performance Optimization
-  Fault Tolerance
-  Load Balancing

##  **TROUBLESHOOTING**

### **Common Issues**

#### **1. CUDA Out of Memory**
bash
# Reduce batch size
config['batch_size'] = 16

# Enable aggressive memory cleanup
config['memory']['cleanup_aggressive'] = true

# Reduce GPU memory fraction
config['performance']['gpu_memory_fraction'] = 0.6


#### **2. Slow Processing**
bash
# Increase worker count
config['processing']['parallel_workers'] = 8

# Enable mixed precision
config['performance']['mixed_precision'] = true

# Optimize batch size
config['processing']['batch_size'] = 64


#### **3. Memory Issues**
bash
# Reduce RAM disk size
config['ram_disk']['size_gb'] = 2

# Enable aggressive cleanup
config['memory']['cleanup_aggressive'] = true

# Reduce worker count
config['processing']['parallel_workers'] = 2


### **Debug Mode**
python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose output
processor = HybridRAGProcessor(config, verbose=True)


##  **PERFORMANCE BENCHMARKS**

### **Expected Performance**
- **CPU Only**: 50-100 files/second
- **GPU Only**: 200-500 files/second
- **Hybrid Mode**: 300-800 files/second
- **With RAM Disk**: 400-1000 files/second

### **Memory Usage**
- **Base System**: 2-4 GB
- **Per 1000 Files**: +1-2 GB
- **Peak Usage**: 6-8 GB (configurable)

### **Scaling Characteristics**
- **Linear Scaling**: Performance scales linearly with worker count
- **Memory Scaling**: Memory usage scales with batch size
- **GPU Scaling**: GPU utilization scales with workload

##  **FUTURE ENHANCEMENTS**

### **Planned Features**
- **Multi-GPU Support**: Distributed processing across multiple GPUs
- **Cloud Integration**: AWS, Azure, GCP support
- **Advanced Models**: Support for larger transformer models
- **Real-time Processing**: Streaming document processing
- **API Server**: REST API for integration

### **Performance Improvements**
- **Quantization**: INT8/FP16 optimization
- **Model Pruning**: Reduced model size for faster inference
- **Distributed Training**: Multi-node training support

##  **API REFERENCE**

### **Core Classes**

#### **HybridRAGProcessor**
python
class HybridRAGProcessor:
    def __init__(self, config: Dict[str, Any])
    def process_files(self, file_paths: List[str], batch_size: int) -> List[ProcessingResult]
    def build_index(self, results: List[ProcessingResult]) -> bool
    def search(self, query: str, top_k: int) -> List[Tuple[int, float]]
    def cleanup(self) -> None


#### **MemoryManager**
python
class MemoryManager:
    def get_system_memory(self) -> Dict[str, float]
    def get_gpu_memory(self) -> Dict[str, float]
    def should_cleanup_memory(self) -> bool
    def cleanup_memory(self) -> None


#### **RAMDiskManager**
python
class RAMDiskManager:
    def create_ram_disk(self) -> bool
    def get_available_space(self) -> int
    def can_fit_file(self, file_size: int) -> bool
    def cleanup_ram_disk(self) -> None


##  **CONTRIBUTING**

### **Development Setup**
bash
# Install development dependencies
pip install -r requirements_hybrid_v4.txt
pip install -r requirements-dev.txt

# Run tests
pytest rag/tests/

# Code formatting
black rag/
flake8 rag/


### **Code Standards**
- **Python**: PEP 8 compliance
- **Documentation**: Google-style docstrings
- **Testing**: 90%+ coverage required
- **Type Hints**: Full type annotation

##  **LICENSE**

This project is licensed under the MIT License - see the LICENSE file for details.

##  **ACKNOWLEDGMENTS**

- **PyTorch Team**: For the excellent deep learning framework
- **Hugging Face**: For the sentence-transformers library
- **Facebook Research**: For FAISS vector similarity search
- **Open Source Community**: For all the supporting libraries

---

##  **GETTING HELP**

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for help and ideas
- **Performance**: Use the benchmark mode to test your setup

---

** Ready to experience the power of hybrid CPU+GPU processing? Start with the quick start guide above!**
