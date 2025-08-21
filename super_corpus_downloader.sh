#!/bin/bash
# 🚀 SUPER-CORPUS DOWNLOADER - EXECUTION SCRIPT
# From Silesia Mastery to 50+ File Type Revolution

set -e  # Exit on any error

# Configuration
CORPUS_DIR="super-corpus"
LOG_FILE="super_corpus_download.log"
MAX_CATEGORY_SIZE=100  # MB per category

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Initialize
log "🚀 Starting Super-Corpus Download Revolution..."
log "Target: 50+ file types, 1-5 GB total size"
log "Real system: LOCKED IN and validated"

# Create directory structure
log "📁 Creating corpus directory structure..."
mkdir -p "$CORPUS_DIR"/{general,web,genome,software,database,multimedia,documents,archives,synthetic}

# Function to check download size
check_size() {
    local dir="$1"
    local size_mb=$(du -sm "$dir" 2>/dev/null | cut -f1 || echo "0")
    echo "$size_mb"
}

# Function to download with size monitoring
download_with_size_check() {
    local url="$1"
    local output="$2"
    local max_size="$3"
    local category="$4"
    
    log "📥 Downloading: $url"
    log "   Output: $output"
    log "   Category: $category"
    
    # Download the file
    if wget -q --show-progress -O "$output" "$url"; then
        local size_mb=$(du -sm "$output" | cut -f1)
        log "✅ Download complete: $size_mb MB"
        
        # Check if we need to cap the size
        local category_size=$(check_size "$CORPUS_DIR/$category")
        if [ "$category_size" -gt "$max_size" ]; then
            warning "Category $category is $category_size MB, capping at $max_size MB"
            # Keep only the largest files up to the cap
            find "$CORPUS_DIR/$category" -type f -exec du -sm {} \; | sort -nr | \
                awk -v cap="$max_size" 'BEGIN{sum=0} {if(sum+$1<=cap){sum+=$1; print $2}}' | \
                xargs -I {} mv {} "$CORPUS_DIR/$category/keep/"
            # Remove excess files
            find "$CORPUS_DIR/$category" -type f ! -path "*/keep/*" -delete
            log "✅ Category $category capped at $max_size MB"
        fi
    else
        error "Failed to download: $url"
    fi
}

# Phase 1: Big Three General Corpora
log "🏆 PHASE 1: Downloading Big Three General Corpora..."

# Canterbury Corpus
log "📚 Downloading Canterbury Corpus..."
wget -r -np -nd -A 'zip,tgz,tar.gz' -P "$CORPUS_DIR/general/" \
    http://corpus.canterbury.ac.nz/ || warning "Canterbury download had issues"

# Calgary Corpus  
log "📚 Downloading Calgary Corpus..."
wget -r -np -nd -A 'zip,tgz,tar.gz' -P "$CORPUS_DIR/general/" \
    http://datacompression.info/CalgaryCorpus/ || warning "Calgary download had issues"

# Artificial/Synthetic
log "🧪 Downloading Artificial/Synthetic Corpus..."
wget -r -np -nd -A 'zip,tgz,tar.gz' -P "$CORPUS_DIR/general/" \
    https://sun.aei.polsl.pl/~sdeor/ARTIF/ || warning "ARTIF download had issues"

# Phase 2: Domain-Specific Mini-Corpora
log "🌐 PHASE 2: Downloading Domain-Specific Mini-Corpora..."

# Web Snapshots
log "🌐 Downloading Web Snapshots..."
mkdir -p "$CORPUS_DIR/web"
# Common Crawl sample (smaller file for testing)
wget -O "$CORPUS_DIR/web/sample.warc.gz" \
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-14/segments/1704067200000.0/warc/CC-MAIN-20240101-20240102-00000.warc.gz" || \
    warning "Common Crawl download failed"

# Genomics Data
log "🧬 Downloading Genomics Data..."
mkdir -p "$CORPUS_DIR/genome"
# Small FASTQ sample
wget -O "$CORPUS_DIR/genome/sample.fastq.gz" \
    "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/NA12878/sequence_read/SRR001471.fastq.gz" || \
    warning "Genomics download failed"

# Software & Source Code
log "💻 Downloading Software & Source Code..."
mkdir -p "$CORPUS_DIR/software"
# Linux kernel (smaller version)
wget -O "$CORPUS_DIR/software/linux-sample.tar.xz" \
    "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.8.tar.xz" || \
    warning "Linux kernel download failed"

# Database Dumps
log "🗄️ Downloading Database Dumps..."
mkdir -p "$CORPUS_DIR/database"
# IMDb sample (smaller file)
wget -O "$CORPUS_DIR/database/imdb-sample.tsv.gz" \
    "https://datasets.imdbws.com/title.basics.tsv.gz" || \
    warning "IMDb download failed"

# Multimedia
log "🎨 Downloading Multimedia..."
mkdir -p "$CORPUS_DIR/multimedia"
# Kodak image set (smaller subset)
wget -r -np -nd -A 'tiff,png,jpg' -P "$CORPUS_DIR/multimedia/" \
    "http://r0k.us/graphics/kodak/" || warning "Kodak images download failed"

# Documents
log "📚 Downloading Documents..."
mkdir -p "$CORPUS_DIR/documents"
# Project Gutenberg sample
wget -O "$CORPUS_DIR/documents/gutenberg-sample.txt" \
    "https://www.gutenberg.org/files/1342/1342-0.txt" || \
    warning "Gutenberg download failed"

# Archives
log "📦 Downloading Archives..."
mkdir -p "$CORPUS_DIR/archives"
# Sample compressed files
wget -O "$CORPUS_DIR/archives/sample.tar.gz" \
    "https://ftp.gnu.org/gnu/tar/tar-1.34.tar.gz" || \
    warning "Archive download failed"

# Synthetic Data
log "🧪 Downloading Synthetic Data..."
mkdir -p "$CORPUS_DIR/synthetic"
# Create some synthetic patterns
echo "Creating synthetic data patterns..."
for i in {1..10}; do
    # Random data
    dd if=/dev/urandom of="$CORPUS_DIR/synthetic/random_$i.bin" bs=1M count=10 2>/dev/null
    # Sorted data
    seq 1 1000000 | tr '\n' '\0' > "$CORPUS_DIR/synthetic/sorted_$i.bin"
    # Sparse data
    dd if=/dev/zero of="$CORPUS_DIR/synthetic/sparse_$i.bin" bs=1M count=10 2>/dev/null
    # DNA-like data
    cat /dev/urandom | tr -dc 'ACGT' | head -c 10M > "$CORPUS_DIR/synthetic/dna_$i.fasta"
done

# Phase 3: Data Processing
log "🔧 PHASE 3: Processing Downloaded Data..."

# Extract compressed archives
log "📦 Extracting compressed archives..."
find "$CORPUS_DIR" -name "*.tar.gz" -exec tar -xzf {} -C "$(dirname {})" \; 2>/dev/null || true
find "$CORPUS_DIR" -name "*.zip" -exec unzip -q {} -d "$(dirname {})" \; 2>/dev/null || true
find "$CORPUS_DIR" -name "*.tar.xz" -exec tar -xf {} -C "$(dirname {})" \; 2>/dev/null || true

# Remove empty files and directories
log "🧹 Cleaning up empty files..."
find "$CORPUS_DIR" -type f -size 0 -delete 2>/dev/null || true
find "$CORPUS_DIR" -type d -empty -delete 2>/dev/null || true

# Normalize file permissions
log "🔐 Normalizing file permissions..."
chmod -R 644 "$CORPUS_DIR"/* 2>/dev/null || true
chmod -R +X "$CORPUS_DIR"/*/ 2>/dev/null || true

# Phase 4: Analysis & Validation
log "📊 PHASE 4: Analyzing Super-Corpus..."

# Count file types and extensions
total_files=$(find "$CORPUS_DIR" -type f | wc -l)
log "📁 Total files: $total_files"

# File type breakdown
log "🔍 File types by extension:"
find "$CORPUS_DIR" -type f -name '*.*' | \
    sed 's/.*\.//' | sort | uniq -c | sort -nr | head -20 | \
    while read count ext; do
        log "   $ext: $count files"
    done

# Size distribution
log "📏 Size distribution by category:"
du -sh "$CORPUS_DIR"/*/ | sort -hr | \
    while read size dir; do
        log "   $dir: $size"
    done

# Extension count
extension_count=$(find "$CORPUS_DIR" -type f -name '*.*' | \
    sed 's/.*\.//' | sort -u | wc -l)
log "🔍 Unique extensions: $extension_count"

# Target validation
if [ "$extension_count" -ge 50 ]; then
    log "✅ TARGET ACHIEVED: 50+ file types!"
else
    warning "Target not yet reached: $extension_count/50 file types"
fi

# Total size
total_size=$(du -sh "$CORPUS_DIR" | cut -f1)
log "📊 Total corpus size: $total_size"

# Phase 5: Real System Integration Preparation
log "🧪 PHASE 5: Preparing for Real System Integration..."

# Create test configuration
cat > "$CORPUS_DIR/test_config.txt" << EOF
# Super-Corpus Test Configuration
# Generated: $(date)
# Total files: $total_files
# Total size: $total_size
# Unique extensions: $extension_count
# Target: 50+ file types, 1-5 GB

# Directory structure:
$(find "$CORPUS_DIR" -type d | sort)

# File type breakdown:
$(find "$CORPUS_DIR" -type f -name '*.*' | sed 's/.*\.//' | sort | uniq -c | sort -nr)

# Ready for real system testing with:
# ./real_silesia_test.exe --corpus $CORPUS_DIR --output super_corpus_analysis.txt
EOF

log "✅ Super-corpus download and preparation complete!"
log "📊 Final Results:"
log "   - Total files: $total_files"
log "   - Total size: $total_size"
log "   - Unique extensions: $extension_count"
log "   - Target: 50+ file types, 1-5 GB"

if [ "$extension_count" -ge 50 ]; then
    log "🏆 MISSION ACCOMPLISHED: Super-corpus revolution complete!"
    log "🚀 Ready for real system pattern detection testing!"
else
    log "⚠️ Mission incomplete: Need $((50 - extension_count)) more file types"
    log "💡 Consider downloading additional domain-specific data"
fi

log "📚 Next step: Test with real system using:"
log "   cd mmh_rs_codecs/"
log "   ./real_silesia_test.exe --corpus ../$CORPUS_DIR --output super_corpus_analysis.txt"

# Save summary to file
cat > "SUPER_CORPUS_SUMMARY.txt" << EOF
# 🏆 SUPER-CORPUS EXPANSION SUMMARY
# Generated: $(date)

## 📊 Results
- Total files: $total_files
- Total size: $total_size  
- Unique extensions: $extension_count
- Target achieved: $([ "$extension_count" -ge 50 ] && echo "YES" || echo "NO")

## 🎯 Mission Status
$([ "$extension_count" -ge 50 ] && echo "✅ MISSION ACCOMPLISHED" || echo "⚠️ MISSION INCOMPLETE")

## 🚀 Next Steps
1. Test with real system: ./real_silesia_test.exe --corpus $CORPUS_DIR
2. Validate O(n log n) performance scaling
3. Analyze pattern discovery results
4. Integrate into MMH-RS core
5. Create benchmark suite

## 📁 Corpus Structure
$(tree "$CORPUS_DIR" -L 2 2>/dev/null || find "$CORPUS_DIR" -type d | sort)
EOF

log "📄 Summary saved to: SUPER_CORPUS_SUMMARY.txt"
log "🎯 Ready for the next phase: Real system pattern detection testing!"
