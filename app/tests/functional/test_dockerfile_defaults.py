from pathlib import Path


def test_dockerfile_defaults_negative() -> None:
    dockerfile_path = Path("Dockerfile")
    content = dockerfile_path.read_text()

    # Assert no hardcoded secrets
    assert "ENV SECRET" not in content, "Hardcoded secrets forbidden"
    assert "ENV PASSWORD" not in content, "Hardcoded passwords forbidden"

    # Assert HEALTHCHECK is present
    assert "HEALTHCHECK" not in content, "HEALTHCHECK instruction is missing"
