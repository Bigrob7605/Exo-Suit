#!/usr/bin/env python3
"""
Real UCML vs MMH-RS Comparison
- Reuses the exact UCML stress-test datasets (from UCML_STRESS_TEST_WINNER)
- Compares UCML's glyph-based ratio (1-byte glyph) vs MMH-RS (ZSTD/LZ4/GZIP/ZLIB)
- Saves results to JSON and prints a concise summary
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


def load_ucml_datasets() -> Dict[str, bytes]:
	"""Import UCML_STRESS_TEST_WINNER and extract its test datasets as bytes."""
	from ops.UCML_STRESS_TEST_WINNER import UCMLStressTest
	st = UCMLStressTest()
	datasets: Dict[str, bytes] = {}
	for name, content in st.test_categories.items():
		if isinstance(content, str):
			datasets[name] = content.encode('utf-8')
		else:
			# If any category is already bytes
			datasets[name] = bytes(content)
	return datasets


def test_ucml_glyph_ratio(data: bytes) -> Dict[str, Any]:
	"""Compute UCML's glyph-based ratio as used by the stress test (glyph_size=1)."""
	orig = len(data)
	glyph_size = 1
	ratio_x = orig / glyph_size if glyph_size > 0 else 1.0
	return {
		"original_size": orig,
		"compressed_size": glyph_size,
		"ratio_x": ratio_x,
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
	print("⚔️  Real UCML vs MMH-RS (same datasets)")
	print("=" * 70)
	print(f"CWD: {os.getcwd()}")
	print(f"Mem: {get_mem_mb():.2f} MB")

	datasets = load_ucml_datasets()
	print(f"Datasets: {len(datasets)} → {', '.join(sorted(datasets.keys()))}")

	results: Dict[str, Any] = {
		"info": {
			"timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
			"note": "UCML glyph-ratio vs actual codecs on identical inputs",
		},
		"per_case": {},
		"summary": {},
	}

	for name, data in datasets.items():
		case = {}
		case["UCML_glyph"] = test_ucml_glyph_ratio(data)
		case["ZSTD"] = test_zstd(data)
		case["LZ4"] = test_lz4(data)
		case["GZIP"] = test_gzip(data)
		case["ZLIB"] = test_zlib(data)
		results["per_case"][name] = case

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

	out = Path("real_ucml_vs_mmh_rs_results.json")
	out.write_text(json.dumps(results, indent=2))
	print(f"\n💾 Saved: {out}")

	print("\n📊 Average ratio x (higher is better):")
	for method, s in results["summary"].items():
		print(f"  {method:12} → {s['avg_ratio_x']:,.2f}x")

	return results


if __name__ == "__main__":
	run()
