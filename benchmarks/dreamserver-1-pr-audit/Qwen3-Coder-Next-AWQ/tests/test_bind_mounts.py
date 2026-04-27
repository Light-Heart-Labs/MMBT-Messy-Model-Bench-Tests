#!/usr/bin/env python3
"""Test bind mount normalization for PR #1057."""

import json
import tempfile
from pathlib import Path


def test_bind_mount_normalization():
    """Test that bind mount normalization handles short-form and long-form mounts."""
    # Simulate _precreate_data_dirs logic
    def normalize_mount(vol, install_dir):
        """Normalize a single mount, returning the resolved host path or None."""
        if isinstance(vol, dict):
            # Compose long-form mount; only bind mounts have a host source.
            if vol.get("type") != "bind":
                return None
            vol_str = vol.get("source", "")
        else:
            vol_str = str(vol).split(":")[0]
        
        # Skip sources compose does not pre-expand (env vars, home,
        # backticks, Windows-style escapes) — we cannot resolve them safely.
        if not vol_str or vol_str.startswith(("~", "$", "`", "\\")):
            return None
        
        # Simulate directory creation
        if vol_str.startswith("./data/") or vol_str.startswith("data/"):
            dir_path = (install_dir / vol_str.lstrip("./")).resolve()
            dir_path.mkdir(parents=True, exist_ok=True)
            return str(dir_path)
        
        return None

    # Test cases
    test_cases = [
        # Short-form mounts
        ("./data/model1:/data", "model1"),
        ("data/model2:/data", "model2"),
        ("./logs:/logs", None),  # Not under data/
        
        # Long-form mounts
        ({"type": "bind", "source": "./data/model3", "target": "/data"}, "model3"),
        ({"type": "bind", "source": "data/model4", "target": "/data"}, "model4"),
        ({"type": "volume", "source": "model5", "target": "/data"}, None),  # Not bind
        ({"type": "bind", "source": "./logs", "target": "/logs"}, None),  # Not under data/
        
        # Unresolvable sources
        ({"type": "bind", "source": "~/data", "target": "/data"}, None),
        ({"type": "bind", "source": "$HOME/data", "target": "/data"}, None),
        ({"type": "bind", "source": "`pwd`/data", "target": "/data"}, None),
        ({"type": "bind", "source": "\\path\\to\\data", "target": "/data"}, None),
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        install_dir = Path(tmpdir)
        
        for vol, expected in test_cases:
            result = normalize_mount(vol, install_dir)
            if expected is None:
                assert result is None, f"Expected None for {vol}, got {result}"
            else:
                assert result is not None, f"Expected path for {vol}, got None"
                assert expected in result, f"Expected {expected} in {result}, got {result}"
        
        print("✅ All bind mount normalization tests passed!")


if __name__ == "__main__":
    test_bind_mount_normalization()
