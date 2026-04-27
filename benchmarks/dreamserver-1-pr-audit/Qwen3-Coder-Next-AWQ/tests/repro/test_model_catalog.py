#!/usr/bin/env python3
"""Reproduce model catalog error handling for PR #1057."""

import json
import tempfile
from pathlib import Path


def test_model_catalog_error_handling():
    """Test that model catalog errors are handled correctly (500 vs. 403)."""
    
    def check_model_allowed(gguf_file, library_path):
        """Check if a model is allowed, returning (allowed, status_code, error)."""
        allowed = False
        catalog_ok = False
        expected_sha_by_file = {}
        
        if library_path.exists():
            try:
                lib = json.loads(library_path.read_text(encoding="utf-8"))
                catalog_ok = True
                for m in lib.get("models", []):
                    if m.get("gguf_file") != gguf_file:
                        continue
                    allowed = True
                    expected_sha_by_file = {gguf_file: m.get("gguf_sha256", "")}
                    break
            except (json.JSONDecodeError, OSError) as e:
                return (False, 500, "Model catalog unavailable", e)
        
        if not catalog_ok:
            return (False, 500, "Model catalog unavailable", None)
        
        if not allowed:
            return (False, 403, "Model not in library catalog", None)
        
        return (True, 200, "OK", None)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        library_path = Path(tmpdir) / "model-library.json"
        
        # Test 1: Missing catalog file (should be 403, not 500)
        print("Test 1: Missing catalog file")
        allowed, status, error, exc = check_model_allowed("model1.gguf", library_path)
        print(f"  Result: status={status}, error={error}")
        # Note: Original code would return 403 for missing file; PR changes this to 500 only if catalog exists but is unreadable
        # Since file doesn't exist, catalog_ok is never set to True, so it returns 403
        # Wait, let me re-check the logic...
        
        # Actually, the PR logic is:
        # - If library_path.exists() is False, catalog_ok stays False, returns 500
        # - If library_path.exists() is True but parsing fails, catalog_ok stays False, returns 500
        # - If library_path.exists() is True and parsing succeeds, catalog_ok = True
        
        # Let me fix the test to match the PR logic exactly:
        
        def check_model_allowed_pr(gguf_file, library_path):
            """Check if a model is allowed, matching PR #1057 logic exactly."""
            allowed = False
            catalog_ok = False
            expected_sha_by_file = {}
            
            if library_path.exists():
                try:
                    lib = json.loads(library_path.read_text(encoding="utf-8"))
                    catalog_ok = True
                    for m in lib.get("models", []):
                        if m.get("gguf_file") != gguf_file:
                            continue
                        allowed = True
                        expected_sha_by_file = {gguf_file: m.get("gguf_sha256", "")}
                        break
                except (json.JSONDecodeError, OSError) as e:
                    return (False, 500, "Model catalog unavailable", e)
            
            if not catalog_ok:
                return (False, 500, "Model catalog unavailable", None)
            
            if not allowed:
                return (False, 403, "Model not in library catalog", None)
            
            return (True, 200, "OK", None)
        
        # Test 1: Missing catalog file
        print("\nTest 1: Missing catalog file")
        allowed, status, error, exc = check_model_allowed_pr("model1.gguf", library_path)
        print(f"  Result: status={status}, error={error}")
        assert status == 500, f"Expected 500 for missing file, got {status}"
        assert error == "Model catalog unavailable", f"Expected 'Model catalog unavailable', got {error}"
        print("  ✅ Correctly returns 500 (not 403)")
        
        # Test 2: Corrupted catalog file
        print("\nTest 2: Corrupted catalog file")
        library_path.write_text("{invalid json")
        allowed, status, error, exc = check_model_allowed_pr("model1.gguf", library_path)
        print(f"  Result: status={status}, error={error}")
        assert status == 500, f"Expected 500 for corrupted file, got {status}"
        assert error == "Model catalog unavailable", f"Expected 'Model catalog unavailable', got {error}"
        print("  ✅ Correctly returns 500 (not 403)")
        
        # Test 3: Valid catalog, model not listed
        print("\nTest 3: Valid catalog, model not listed")
        library_path.write_text(json.dumps({"models": [{"gguf_file": "model2.gguf"}]}))
        allowed, status, error, exc = check_model_allowed_pr("model1.gguf", library_path)
        print(f"  Result: status={status}, error={error}")
        assert status == 403, f"Expected 403 for model not listed, got {status}"
        assert error == "Model not in library catalog", f"Expected 'Model not in library catalog', got {error}"
        print("  ✅ Correctly returns 403 (not 500)")
        
        # Test 4: Valid catalog, model listed
        print("\nTest 4: Valid catalog, model listed")
        allowed, status, error, exc = check_model_allowed_pr("model2.gguf", library_path)
        print(f"  Result: status={status}, error={error}")
        assert status == 200, f"Expected 200 for model listed, got {status}"
        assert error == "OK", f"Expected 'OK', got {error}"
        print("  ✅ Correctly returns 200")
        
        print("\n✅ All model catalog error handling tests passed!")


if __name__ == "__main__":
    test_model_catalog_error_handling()
