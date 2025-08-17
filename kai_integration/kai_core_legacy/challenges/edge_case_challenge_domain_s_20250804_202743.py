def edge_case_challenge_domain_s(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Edge case challenge: Test edge_case handling for code domain_s

    This challenge tests how the system handles extreme or unexpected inputs.
    """
    try:
        # Edge case: Empty data
        if data.size == 0:
            return {
                "challenge_type": "edge_case",
                "challenge_name": "edge_case_challenge_domain_s",
                "description": "Test edge_case handling for code domain_s",
                "expected_failure": True,
                "result": {"error": "Empty data array", "handled_gracefully": True},
            }

        # Edge case: Single value
        if data.size == 1:
            return {
                "challenge_type": "edge_case",
                "challenge_name": "edge_case_challenge_domain_s",
                "description": "Test edge_case handling for code domain_s",
                "expected_failure": False,
                "result": {"single_value": float(data[0]), "handled_gracefully": True},
            }

        # Edge case: All identical values
        if np.all(data == data[0]):
            return {
                "challenge_type": "edge_case",
                "challenge_name": "edge_case_challenge_domain_s",
                "description": "Test edge_case handling for code domain_s",
                "expected_failure": False,
                "result": {
                    "all_identical": True,
                    "variance": 0.0,
                    "handled_gracefully": True,
                },
            }

        # Edge case: NaN values
        if np.any(np.isnan(data)):
            return {
                "challenge_type": "edge_case",
                "challenge_name": "edge_case_challenge_domain_s",
                "description": "Test edge_case handling for code domain_s",
                "expected_failure": True,
                "result": {
                    "nan_count": int(np.sum(np.isnan(data))),
                    "handled_gracefully": True,
                },
            }

        # Edge case: Infinite values
        if np.any(np.isinf(data)):
            return {
                "challenge_type": "edge_case",
                "challenge_name": "edge_case_challenge_domain_s",
                "description": "Test edge_case handling for code domain_s",
                "expected_failure": True,
                "result": {
                    "inf_count": int(np.sum(np.isinf(data))),
                    "handled_gracefully": True,
                },
            }

        return {
            "challenge_type": "edge_case",
            "challenge_name": "edge_case_challenge_domain_s",
            "description": "Test edge_case handling for code domain_s",
            "expected_failure": False,
            "result": {"handled_gracefully": True, "data_shape": data.shape},
        }

    except Exception as e:
        return {
            "challenge_type": "edge_case",
            "challenge_name": "edge_case_challenge_domain_s",
            "description": "Test edge_case handling for code domain_s",
            "expected_failure": True,
            "result": {"error": str(e), "handled_gracefully": False},
        }
