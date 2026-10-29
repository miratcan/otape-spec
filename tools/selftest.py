#!/usr/bin/env python3
"""Repository self-test, run by CI and before every release.

    python3 tools/selftest.py

1. The JSON Schema is a valid draft 2020-12 schema (needs `jsonschema`).
2. Every example validates as expected: `invalid-*` files must be rejected,
   everything else must pass.
3. The SVG templates are up to date with geometry/otape-geometry-1.0.json.

Part of the oTAPE specification · © 2026 Jan Osio · CC BY 4.0
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import otape_validate  # noqa: E402

failures: list[str] = []

# 1. Schema
try:
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(json.loads((ROOT / "schema" / "otape-manifest-1.0.schema.json").read_text()))
    print("ok   schema is a valid JSON Schema 2020-12 document")
except ImportError:
    failures.append("jsonschema is not installed (pip install -r tools/requirements.txt)")
except Exception as e:  # noqa: BLE001
    failures.append(f"schema: {e}")

# 2. Examples
examples = sorted((ROOT / "examples").rglob("*.json")) + sorted((ROOT / "examples").rglob("*.otape"))
for path in examples:
    report = otape_validate.validate(path)
    expect_valid = not path.name.startswith("invalid-")
    if report.valid == expect_valid:
        print(f"ok   {path.relative_to(ROOT)} is {'valid' if expect_valid else 'rejected'}")
    else:
        failures.append(f"{path.relative_to(ROOT)}: expected {'valid' if expect_valid else 'invalid'}; "
                        + "; ".join(report.errors or ["no errors reported"]))

# 3. Templates
with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "spec"
    (copy / "tools").mkdir(parents=True)
    (copy / "geometry").mkdir()
    (copy / "tools" / "make_templates.py").write_text((ROOT / "tools" / "make_templates.py").read_text())
    (copy / "geometry" / "otape-geometry-1.0.json").write_text((ROOT / "geometry" / "otape-geometry-1.0.json").read_text())
    subprocess.run([sys.executable, str(copy / "tools" / "make_templates.py")], check=True, stdout=subprocess.DEVNULL)
    for svg in sorted((copy / "templates").glob("*.svg")):
        committed = ROOT / "templates" / svg.name
        if not committed.exists() or committed.read_text() != svg.read_text():
            failures.append(f"templates/{svg.name} is out of date: run python3 tools/make_templates.py")
        else:
            print(f"ok   templates/{svg.name} matches the geometry")

if failures:
    print("\nFAILED")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("\nall checks passed")
