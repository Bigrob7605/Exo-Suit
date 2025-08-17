def data_manipulation_challenge_domain_s(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    Data manipulation challenge: Test data_manipulation handling for code domain_s

    This challenge tests if the system can detect data manipulation.
    """
    try:
        # Check for data manipulation indicators

        # 1. Check for suspicious patterns
        suspicious_patterns = []

        # All values identical
        if np.all(data == data[0]):
            suspicious_patterns.append("all_identical")

        # Perfect correlation
        if data.ndim == 2 and data.shape[1] >= 2:
            corr = np.corrcoef(data[:, 0], data[:, 1])[0, 1]
            if abs(corr) > 0.99:
                suspicious_patterns.append("perfect_correlation")

        # Round numbers only
        if np.all(np.round(data) == data):
            suspicious_patterns.append("all_round_numbers")

        # 2. Check for statistical anomalies
        anomalies = []

        # Too perfect distribution
        if data.size > 100:
            mean_val = np.mean(data)
            std_val = np.std(data)
            z_scores = np.abs((data - mean_val) / std_val)
            if np.max(z_scores) < 2.0:  # No outliers
                anomalies.append("too_perfect_distribution")

        # 3. Check for data fabrication indicators
        fabrication_indicators = []

        # Benford's law violation
        if np.all(data > 0):
            first_digits = [int(str(abs(x))[0]) for x in data.flatten()]
            digit_counts = np.bincount(first_digits, minlength=10)[1:]
            expected_benford = np.array(
                [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
            )
            if len(digit_counts) >= 9:
                benford_violation = np.sum(
                    np.abs(
                        digit_counts / len(first_digits)
                        - expected_benford[: len(digit_counts)]
                    )
                )
                if benford_violation > 0.5:
                    fabrication_indicators.append("benford_law_violation")

        manipulation_detected = (
            len(suspicious_patterns) > 0
            or len(anomalies) > 0
            or len(fabrication_indicators) > 0
        )

        return {
            "challenge_type": "data_manipulation",
            "challenge_name": "data_manipulation_challenge_domain_s",
            "description": "Test data_manipulation handling for code domain_s",
            "expected_failure": manipulation_detected,
            "result": {
                "suspicious_patterns": suspicious_patterns,
                "anomalies": anomalies,
                "fabrication_indicators": fabrication_indicators,
                "manipulation_detected": manipulation_detected,
                "data_hash": hashlib.sha256(data.tobytes()).hexdigest(),
            },
        }

    except Exception as e:
        return {
            "challenge_type": "data_manipulation",
            "challenge_name": "data_manipulation_challenge_domain_s",
            "description": "Test data_manipulation handling for code domain_s",
            "expected_failure": True,
            "result": {"error": str(e), "handled_gracefully": False},
        }
