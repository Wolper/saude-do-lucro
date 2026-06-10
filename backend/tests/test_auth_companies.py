from pathlib import Path


def test_auth_dependencies_are_pinned_for_passlib_bcrypt_compatibility() -> None:
    requirements = Path(__file__).resolve().parents[1] / "requirements.txt"

    pinned_dependencies = set(requirements.read_text(encoding="utf-8").splitlines())

    assert "passlib[bcrypt]==1.7.4" in pinned_dependencies
    assert "bcrypt==4.0.1" in pinned_dependencies
