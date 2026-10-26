#!/usr/bin/env python3
"""Read safetensors headers without loading tensor data or executing model code."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

MAX_HEADER_BYTES = 64 * 1024 * 1024
DTYPE_BYTES = {"BOOL": 1, "U8": 1, "I8": 1, "F8_E4M3": 1, "F8_E5M2": 1,
               "I16": 2, "U16": 2, "F16": 2, "BF16": 2, "I32": 4,
               "U32": 4, "F32": 4, "I64": 8, "U64": 8, "F64": 8}


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key in safetensors header: {key}")
        obj[key] = value
    return obj


def inspect(path: Path, limit: int = 100, hash_file: bool = False) -> dict:
    if limit < 0:
        raise ValueError("--limit cannot be negative")
    file_size = path.stat().st_size
    if file_size < 8:
        raise ValueError("File too short to be safetensors")
    with path.open("rb") as f:
        size_data = f.read(8)
        (header_size,) = struct.unpack("<Q", size_data)
        if header_size == 0 or header_size > MAX_HEADER_BYTES or header_size + 8 > file_size:
            raise ValueError("Invalid or unexpectedly large safetensors header")
        payload = f.read(header_size)
        if len(payload) != header_size:
            raise ValueError("Truncated safetensors header")
    data_start = 8 + header_size
    header = json.loads(payload.decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    if not isinstance(header, dict):
        raise ValueError("Expected object at root of safetensors header")
    metadata = header.pop("__metadata__", {})
    if not isinstance(metadata, dict):
        raise ValueError("Malformed metadata in safetensors header")
    details = []
    total_elements = 0
    warnings = []
    for name, record in sorted(header.items()):
        if not isinstance(record, dict):
            raise ValueError(f"Malformed tensor entry for {name}")
        shape, dtype, offsets = record.get("shape"), record.get("dtype"), record.get("data_offsets")
        if (not isinstance(shape, list) or not all(type(x) is int and x >= 0 for x in shape)
                or not isinstance(dtype, str) or not isinstance(offsets, list) or len(offsets) != 2
                or not all(type(x) is int and x >= 0 for x in offsets)):
            raise ValueError(f"Invalid shape/dtype/offsets for {name}")
        start, end = offsets
        if start > end or end > file_size - data_start:
            raise ValueError(f"Tensor {name} has offsets outside data payload")
        elements = 1
        for x in shape:
            elements *= x
        total_elements += elements
        if dtype in DTYPE_BYTES and elements * DTYPE_BYTES[dtype] != end-start:
            warnings.append(f"{name}: expected bytes ({dtype}) do not match declared data interval")
        if len(details) < limit:
            details.append({"name": name, "shape": shape, "dtype": dtype,
                            "data_offsets": offsets, "elements": elements})
    result = {"path": str(path), "file_size_bytes": file_size,
              "header_bytes": header_size, "tensor_count": len(header),
              "tensors_shown": len(details), "total_declared_elements": total_elements,
              "metadata": metadata, "tensors": details, "warnings": warnings,
              "note": "Header evidence only; does not recover computational graph or training history."}
    if hash_file:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        result["sha256"] = h.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--limit", type=int, default=100, help="Max tensor records to include")
    parser.add_argument("--hash", action="store_true", help="Read full file and compute SHA-256")
    parser.add_argument("--output", type=Path, help="Write JSON result here; otherwise print to stdout")
    args = parser.parse_args()
    try:
        result = inspect(args.path, args.limit, args.hash)
        report = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(report, encoding="utf-8")
            print(f"Read {result['tensor_count']} tensor declarations; wrote {args.output}")
        else:
            print(report, end="")
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as e:
        parser.exit(2, f"error: {e}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
