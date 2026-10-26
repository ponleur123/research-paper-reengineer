"""Self-contained smoke tests for bundled tool scripts."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SkillToolsTests(unittest.TestCase):
    def test_init_case_non_destructive(self):
        app = load_script("init_case")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "trial"
            created = app.init_case("My Paper", output)
            self.assertEqual(len(created), 5)
            self.assertEqual(json.loads((output / "case.json").read_text())["title"], "My Paper")
            (output / "evidence.csv").write_text("USER DATA\n")
            self.assertEqual(len(app.init_case("New Title", output)), 0)
            self.assertEqual((output / "evidence.csv").read_text(), "USER DATA\n")

    def test_empty_evidence(self):
        app = load_script("audit_evidence")
        errors, warnings, counts, size = app.audit(ROOT / "assets" / "evidence.csv")
        self.assertEqual(errors, [])
        self.assertEqual(size, 0)
        self.assertTrue(warnings)

    def test_audit_catches_missing_source(self):
        app = load_script("audit_evidence")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.csv"
            path.write_text((ROOT / "assets" / "evidence.csv").read_text() +
                            'C001,"Model sums views",paper,,,statement,observed,T001,\n')
            errors, _, _, _ = app.audit(path)
            self.assertTrue(any("source_locator" in e for e in errors))

    def test_safetensors_header_and_bounds(self):
        app = load_script("inspect_safetensors")
        header = json.dumps({"weight": {"dtype": "F32", "shape": [2],
                                        "data_offsets": [0, 8]}}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "weights.safetensors"
            path.write_bytes(struct.pack("<Q", len(header)) + header + b"\0" * 8)
            result = app.inspect(path, limit=10, hash_file=True)
            self.assertEqual(result["tensor_count"], 1)
            self.assertEqual(result["tensors"][0]["shape"], [2])
            self.assertEqual(len(result["sha256"]), 64)
            bad_header = json.dumps({"weight": {"dtype": "F32", "shape": [3],
                                                "data_offsets": [0, 12]}}).encode()
            path.write_bytes(struct.pack("<Q", len(bad_header)) + bad_header + b"\0" * 8)
            with self.assertRaises(ValueError):
                app.inspect(path)

    def test_compare_numpy(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy not installed")
        app = load_script("compare_arrays")
        a = {"x": np.asarray([[1, 2]], dtype=np.float32)}
        b = {"x": np.asarray([[1.000001, 2]], dtype=np.float32)}
        c = {"x": np.asarray([[3, 2]], dtype=np.float32)}
        self.assertTrue(app.compare(a, b, np, 1e-5, 1e-4)[0])
        self.assertFalse(app.compare(a, c, np, 1e-5, 1e-4)[0])


if __name__ == "__main__":
    unittest.main()
