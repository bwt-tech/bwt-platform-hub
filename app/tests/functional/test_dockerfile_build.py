from pathlib import Path


def test_dockerfile_build_positive() -> None:
    dockerfile_path = Path("Dockerfile")
    assert dockerfile_path.exists(), "Dockerfile must exist"

    content = dockerfile_path.read_text()
    assert "python:3.14" in content, "Must use python 3.14"
    assert "EXPOSE 8080" in content, "Must expose port 8080"
    assert "uvicorn" in content and "8080" in content, "Must start uvicorn on port 8080"
