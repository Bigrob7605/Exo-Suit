# 🧪 MMH-RS Real Tensor Validation Report

**Date:** 2025-08-18 19:38:05
**Total Tensors Tested:** 6

## 📈 Overall Statistics
- **Total Original Size:** 1.89 MB
- **Total Compressed Size:** 7.15 MB
- **Overall Compression Ratio:** 0.26x

## 🚀 Compression Method Performance
### GZIP
- **Average Compression Ratio:** 1.08x
- **Average Speed:** 24.26 MB/s

### ZLIB
- **Average Compression Ratio:** 1.08x
- **Average Speed:** 31.99 MB/s

### ZSTD
- **Average Compression Ratio:** 1.08x
- **Average Speed:** 514.84 MB/s

### LZ4
- **Average Compression Ratio:** 1.00x
- **Average Speed:** 2341.25 MB/s

## 🔍 Individual Tensor Results
### tensor_0_1000
- **Shape:** (1000,)
- **Size:** 0.00 MB
- **Pattern Score:** 0.001

  - **GZIP:** 1.06x ratio, 3.68 MB/s
  - **ZLIB:** 1.07x ratio, 42.22 MB/s
  - **ZSTD:** 1.07x ratio, 2.81 MB/s
  - **LZ4:** 0.99x ratio, 2.15 MB/s

### tensor_1_100x100
- **Shape:** (100, 100)
- **Size:** 0.04 MB
- **Pattern Score:** 0.000

  - **GZIP:** 1.08x ratio, 40.34 MB/s
  - **ZLIB:** 1.08x ratio, 42.52 MB/s
  - **ZSTD:** 1.08x ratio, 289.86 MB/s
  - **LZ4:** 1.00x ratio, 4324.32 MB/s

### tensor_2_50x50x50
- **Shape:** (50, 50, 50)
- **Size:** 0.48 MB
- **Pattern Score:** 0.000

  - **GZIP:** 1.08x ratio, 25.09 MB/s
  - **ZLIB:** 1.08x ratio, 28.58 MB/s
  - **ZSTD:** 1.08x ratio, 745.43 MB/s
  - **LZ4:** 1.00x ratio, 2793.30 MB/s

### tensor_3_20x20x20x20
- **Shape:** (20, 20, 20, 20)
- **Size:** 0.61 MB
- **Pattern Score:** 0.000

  - **GZIP:** 1.08x ratio, 25.24 MB/s
  - **ZLIB:** 1.08x ratio, 28.16 MB/s
  - **ZSTD:** 1.08x ratio, 784.31 MB/s
  - **LZ4:** 1.00x ratio, 2376.97 MB/s

### tensor_4_1000x100
- **Shape:** (1000, 100)
- **Size:** 0.38 MB
- **Pattern Score:** 0.000

  - **GZIP:** 1.08x ratio, 23.43 MB/s
  - **ZLIB:** 1.08x ratio, 27.68 MB/s
  - **ZSTD:** 1.08x ratio, 692.94 MB/s
  - **LZ4:** 1.00x ratio, 2176.87 MB/s

### tensor_5_100x1000
- **Shape:** (100, 1000)
- **Size:** 0.38 MB
- **Pattern Score:** 0.000

  - **GZIP:** 1.08x ratio, 27.77 MB/s
  - **ZLIB:** 1.08x ratio, 22.79 MB/s
  - **ZSTD:** 1.08x ratio, 573.68 MB/s
  - **LZ4:** 1.00x ratio, 2373.89 MB/s
