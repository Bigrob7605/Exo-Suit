def p_hacking_challenge_domain_p(data: np.ndarray, **kwargs) -> Dict[str, Any]:
    """
    P-hacking challenge: Test p_hacking handling for code domain_p

    This challenge tests if the system can detect and prevent p-hacking.
    """
    try:
        # Simulate p-hacking by trying multiple tests
        from scipy import stats

        # Multiple statistical tests (p-hacking attempt)
        tests = []
        p_values = []

        # Test 1: t-test
        if data.ndim == 2 and data.shape[1] >= 2:
            t_stat, p_val = stats.ttest_ind(data[:, 0], data[:, 1])
            tests.append("t_test")
            p_values.append(p_val)

        # Test 2: Mann-Whitney U
        if data.ndim == 2 and data.shape[1] >= 2:
            u_stat, p_val = stats.mannwhitneyu(data[:, 0], data[:, 1])
            tests.append("mann_whitney")
            p_values.append(p_val)

        # Test 3: Wilcoxon signed-rank
        if data.ndim == 2 and data.shape[1] >= 2:
            w_stat, p_val = stats.wilcoxon(data[:, 0], data[:, 1])
            tests.append("wilcoxon")
            p_values.append(p_val)

        # Test 4: Kruskal-Wallis
        if data.ndim == 2 and data.shape[1] >= 3:
            h_stat, p_val = stats.kruskal(*[data[:, i] for i in range(data.shape[1])])
            tests.append("kruskal_wallis")
            p_values.append(p_val)

        # Check for p-hacking (multiple comparisons without correction)
        significant_tests = [p < 0.05 for p in p_values]
        p_hacking_detected = sum(significant_tests) > 1

        # Bonferroni correction
        bonferroni_threshold = 0.05 / len(p_values) if p_values else 0.05
        corrected_significant = [p < bonferroni_threshold for p in p_values]

        return {
            "challenge_type": "p_hacking",
            "challenge_name": "p_hacking_challenge_domain_p",
            "description": "Test p_hacking handling for code domain_p",
            "expected_failure": p_hacking_detected,
            "result": {
                "tests_performed": tests,
                "p_values": [float(p) for p in p_values],
                "significant_without_correction": significant_tests,
                "significant_with_correction": corrected_significant,
                "p_hacking_detected": p_hacking_detected,
                "bonferroni_threshold": float(bonferroni_threshold),
            },
        }

    except Exception as e:
        return {
            "challenge_type": "p_hacking",
            "challenge_name": "p_hacking_challenge_domain_p",
            "description": "Test p_hacking handling for code domain_p",
            "expected_failure": True,
            "result": {"error": str(e), "handled_gracefully": False},
        }
