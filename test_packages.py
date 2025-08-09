try:
    import sentence_transformers
    print("✅ sentence_transformers installed")
except ImportError:
    print("❌ sentence_transformers not installed")

try:
    import faiss
    print("✅ faiss installed")
except ImportError:
    print("❌ faiss not installed")

try:
    import numpy
    print("✅ numpy installed")
except ImportError:
    print("❌ numpy not installed")
