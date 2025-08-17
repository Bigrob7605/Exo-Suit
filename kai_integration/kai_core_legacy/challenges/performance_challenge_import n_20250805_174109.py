def performance_challenge_import_n(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Performance challenge: Test performance handling for code import n

    This challenge tests system performance under stress.
    """
    try:
        import time

        start_time = time.time()

        # Performance stress test
        # Large data processing
        if data.size > 10000:
            # Complex computation
            result = np.linalg.eigvals(data.reshape(-1, min(100, data.size)))
            computation_time = time.time() - start_time

            # Check for timeout
            timeout_threshold = 30  # seconds
            timed_out = computation_time > timeout_threshold

            return {
                "challenge_type": "performance",
                "challenge_name": "performance_challenge_import_n",
                "description": "Test performance handling for code import n",
                "expected_failure": timed_out,
                "result": {
                    "computation_time": float(computation_time),
                    "timeout_threshold": timeout_threshold,
                    "timed_out": timed_out,
                    "data_size": data.size,
                    "memory_usage": "high" if data.size > 100000 else "normal",
                },
            }
        else:
            # Small data - should be fast
            computation_time = time.time() - start_time

            return {
                "challenge_type": "performance",
                "challenge_name": "performance_challenge_import_n",
                "description": "Test performance handling for code import n",
                "expected_failure": False,
                "result": {
                    "computation_time": float(computation_time),
                    "performance_adequate": computation_time < 1.0,
                    "data_size": data.size,
                },
            }

    except Exception as e:
        return {
            "challenge_type": "performance",
            "challenge_name": "performance_challenge_import_n",
            "description": "Test performance handling for code import n",
            "expected_failure": True,
            "result": {"error": str(e), "handled_gracefully": False},
        }
