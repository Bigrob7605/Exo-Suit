#!/usr/bin/env python3
"""
Real-World Data Compression Test
Tests UCML vs MMH-RS on actual project files, not synthetic data
"""
import os
import sys
import time
import json
import gzip
import zlib
import psutil
from pathlib import Path
from typing import Dict, Any, List

# Allow importing from project root 'ops'
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


def get_mem_mb() -> float:
	proc = psutil.Process(os.getpid())
	return proc.memory_info().rss / (1024 * 1024)


def load_real_data() -> Dict[str, bytes]:
	"""Load real project files for testing"""
	datasets = {}
	
	# Real project files
	real_files = [
		"rag/test_data.txt",
		"README.md", 
		"ops/V5_SYSTEM_STATUS.md",
		"ops/UCML_COMPRESSION_CLEAR_WINNER_ACHIEVEMENT_REPORT.md"
	]
	
	for file_path in real_files:
		full_path = PROJECT_ROOT / file_path
		if full_path.exists():
			try:
				content = full_path.read_bytes()
				name = Path(file_path).stem
				datasets[name] = content
				print(f"✅ Loaded: {file_path} ({len(content):,} bytes)")
			except Exception as e:
				print(f"❌ Failed to load {file_path}: {e}")
		else:
			print(f"⚠️  File not found: {file_path}")
	
	return datasets


def test_ucml_glyph_ratio(data: bytes) -> Dict[str, Any]:
	"""Compute UCML's glyph-based ratio (same as stress test)"""
	orig = len(data)
	glyph_size = 1  # UCML claims 1-byte glyphs
	ratio_x = orig / glyph_size if glyph_size > 0 else 1.0
	return {
		"original_size": orig,
		"compressed_size": glyph_size,
		"ratio_x": ratio_x,
		"note": "UCML claims 1-byte glyph compression"
	}


def test_zstd(data: bytes) -> Dict[str, Any]:
	try:
		import zstandard as zstd
		start = time.time()
		cctx = zstd.ZstdCompressor(level=3)
		comp = cctx.compress(data)
		dur = time.time() - start
		orig = len(data)
		return {
			"original_size": orig,
			"compressed_size": len(comp),
			"ratio_x": (orig / max(1, len(comp))),
			"speed_mb_s": (orig / (1024 * 1024)) / max(1e-9, dur),
		}
	except Exception as e:
		return {"error": str(e)}


def test_lz4(data: bytes) -> Dict[str, Any]:
	try:
		import lz4.frame
		start = time.time()
		comp = lz4.frame.compress(data, compression_level=1)
		dur = time.time() - start
		orig = len(data)
		return {
			"original_size": orig,
			"compressed_size": len(comp),
			"ratio_x": (orig / max(1, len(comp))),
			"speed_mb_s": (orig / (1024 * 1024)) / max(1e-9, dur),
		}
	except Exception as e:
		return {"error": str(e)}


def test_gzip(data: bytes) -> Dict[str, Any]:
	start = time.time()
	comp = gzip.compress(data, compresslevel=6)
	dur = time.time() - start
	orig = len(data)
	return {
		"original_size": orig,
		"compressed_size": len(comp),
		"ratio_x": (orig / max(1, len(comp))),
		"speed_mb_s": (orig / (1024 * 1024)) / max(1e-9, dur),
	}


def test_zlib(data: bytes) -> Dict[str, Any]:
	start = time.time()
	comp = zlib.compress(data, level=6)
	dur = time.time() - start
	orig = len(data)
	return {
		"original_size": orig,
		"compressed_size": len(comp),
		"ratio_x": (orig / max(1, len(comp))),
		"speed_mb_s": (orig / (1024 * 1024)) / max(1e-9, dur),
	}


def run() -> Dict[str, Any]:
	print("🌍 Real-World Data Compression Test")
	print("=" * 60)
	print(f"CWD: {os.getcwd()}")
	print(f"Mem: {get_mem_mb():.2f} MB")
	print()

	datasets = load_real_data()
	if not datasets:
		print("❌ No real data loaded!")
		return {}
	
	print(f"\n📊 Testing {len(datasets)} real files...")

	results: Dict[str, Any] = {
		"info": {
			"timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
			"note": "UCML vs MMH-RS on REAL project files",
			"files_tested": list(datasets.keys())
		},
		"per_case": {},
		"summary": {},
	}

	for name, data in datasets.items():
		print(f"\n🔍 Testing: {name} ({len(data):,} bytes)")
		case = {}
		case["UCML_glyph"] = test_ucml_glyph_ratio(data)
		case["ZSTD"] = test_zstd(data)
		case["LZ4"] = test_lz4(data)
		case["GZIP"] = test_gzip(data)
		case["ZLIB"] = test_zlib(data)
		results["per_case"][name] = case
		
		# Show immediate results
		ucml_ratio = case["UCML_glyph"]["ratio_x"]
		best_codec = max([k for k in case.keys() if k != "UCML_glyph"], 
						key=lambda k: case[k].get("ratio_x", 0) if "error" not in case[k] else 0)
		best_ratio = case[best_codec].get("ratio_x", 0)
		
		print(f"   UCML claims: {ucml_ratio:,.1f}x")
		print(f"   Best codec: {best_codec} → {best_ratio:.2f}x")
		
		if ucml_ratio > best_ratio * 10:
			print(f"   🚨 UCML claims {ucml_ratio/best_ratio:.1f}x better than reality!")

	# Summaries
	def avg_ratio(method: str) -> float:
		vals: List[float] = []
		for case in results["per_case"].values():
			res = case.get(method, {})
			rx = res.get("ratio_x")
			if isinstance(rx, (int, float)) and rx > 0:
				vals.append(rx)
		return sum(vals) / len(vals) if vals else 0.0

	for method in ["UCML_glyph", "ZSTD", "LZ4", "GZIP", "ZLIB"]:
		results["summary"][method] = {"avg_ratio_x": round(avg_ratio(method), 2)}

	out = Path("real_world_compression_results.json")
	out.write_text(json.dumps(results, indent=2))
	print(f"\n💾 Saved: {out}")

	print("\n📊 Average ratio x (higher is better):")
	for method, s in results["summary"].items():
		print(f"  {method:12} → {s['avg_ratio_x']:,.2f}x")

	return results


if __name__ == "__main__":
	run()
