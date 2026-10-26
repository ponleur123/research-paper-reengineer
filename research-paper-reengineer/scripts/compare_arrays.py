#!/usr/bin/env python3
"""Compare two NumPy .npy or .npz output snapshots for reproducibility."""
import argparse
from pathlib import Path
import sys


def load_arrays(path, np):
    if path.suffix.lower() not in {".npy", ".npz"}:
        raise ValueError(f"Expected .npy or .npz: {path}")
    loaded = np.load(path, allow_pickle=False)
    if isinstance(loaded, np.ndarray):
        return {"array": loaded}
    try:
        return {k: loaded[k] for k in loaded.files}
    finally:
        loaded.close()


def compare(reference, candidate, np, atol, rtol):
    results = []
    if set(reference) != set(candidate):
        return False, [{"key": "(keys)", "reference": sorted(reference),
                        "candidate": sorted(candidate), "pass": False, "reason": "keys differ"}]
    success = True
    for key in sorted(reference):
        a, b = reference[key], candidate[key]
        base = {"key": key, "reference_shape": list(a.shape),
                "candidate_shape": list(b.shape), "reference_dtype": str(a.dtype),
                "candidate_dtype": str(b.dtype)}
        if a.shape != b.shape:
            base.update({"pass": False, "reason": "shape mismatch"})
        elif not np.issubdtype(a.dtype, np.number) or not np.issubdtype(b.dtype, np.number):
            base.update({"pass": False, "reason": "non-numeric array; cannot compare"})
        elif not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
            base.update({"pass": False, "reason": "NaN/Inf present; inspect manually"})
        else:
            dtype = np.complex128 if np.iscomplexobj(a) or np.iscomplexobj(b) else np.float64
            af, bf = a.astype(dtype), b.astype(dtype)
            diff = np.abs(af - bf)
            ok = np.isclose(af, bf, atol=atol, rtol=rtol)
            base.update({"pass": bool(np.all(ok)), "max_abs": float(np.max(diff)) if diff.size else 0.0,
                         "mean_abs": float(np.mean(diff)) if diff.size else 0.0,
                         "pass_fraction": float(np.mean(ok)) if ok.size else 1.0})
        success = success and base["pass"]
        results.append(base)
    return success, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--atol", type=float, default=1e-5)
    parser.add_argument("--rtol", type=float, default=1e-4)
    args = parser.parse_args()
    if args.atol < 0 or args.rtol < 0:
        parser.error("Tolerances must be nonnegative")
    try:
        import numpy as np
    except ImportError:
        parser.exit(2, "NumPy is required: pip install numpy\n")
    try:
        ref = load_arrays(args.reference, np)
        cand = load_arrays(args.candidate, np)
        success, results = compare(ref, cand, np, args.atol, args.rtol)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    for result in results:
        print(f"{result['key']}: {'PASS' if result['pass'] else 'FAIL'} {result}")
    print(f"Numerical parity: {'PASS' if success else 'FAIL'} (atol={args.atol}, rtol={args.rtol})")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
