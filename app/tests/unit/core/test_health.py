from app.src.core.health import get_health_status


def test_get_health_status_returns_healthy_dict() -> None:
    result = get_health_status()
    assert isinstance(result, dict)
    assert result == {"status": "healthy"}
