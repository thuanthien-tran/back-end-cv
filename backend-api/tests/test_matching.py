from app.matching.engine import calculate_matching, get_compatibility_level


def test_matching_engine_basic():
    cv = "Python FastAPI PostgreSQL Docker 3 years experience Bachelor"
    jd = "Need Python FastAPI PostgreSQL Redis Docker 2 years experience"
    result = calculate_matching(cv, jd)
    assert result["matching_score"] > 0
    assert "python" in result["matched_skills"]
    assert "redis" in result["missing_skills"]
    assert "compatibility" in result
    assert "score_breakdown" in result
    assert result["compatibility"]["level"] in [
        "Excellent Fit", "Strong Fit", "Medium Fit", "Weak Fit", "Not Recommended"
    ]


def test_score_breakdown_weights():
    cv = "Python FastAPI PostgreSQL Docker"
    jd = "Need Python FastAPI PostgreSQL Redis Docker AWS"
    result = calculate_matching(cv, jd)
    breakdown = result["score_breakdown"]
    total_weight = sum(item["weight"] for item in breakdown.values())
    assert total_weight == 100


def test_compatibility_levels():
    assert get_compatibility_level(90)["level"] == "Excellent Fit"
    assert get_compatibility_level(75)["level"] == "Strong Fit"
    assert get_compatibility_level(60)["level"] == "Medium Fit"
    assert get_compatibility_level(45)["level"] == "Weak Fit"
    assert get_compatibility_level(30)["level"] == "Not Recommended"
