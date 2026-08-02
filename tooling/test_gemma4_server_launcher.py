from pathlib import Path


ROOT = Path(__file__).resolve().parent


def test_native_envelope_transport_timeout_is_enforced():
    candidates = [
        ROOT / "deployments" / "gemma4-31b-q4-tower2" / "run-gemma4-server.sh",
        ROOT / "run-gemma4-server.sh",
    ]
    launcher_path = next(path for path in candidates if path.is_file())
    launcher = launcher_path.read_text()
    assert 'HTTP_TIMEOUT="${GEMMA_HTTP_TIMEOUT:-14400}"' in launcher
    assert "HTTP_TIMEOUT < 14400" in launcher
    assert '--timeout "$HTTP_TIMEOUT"' in launcher
    assert "--timeout 3600" not in launcher
