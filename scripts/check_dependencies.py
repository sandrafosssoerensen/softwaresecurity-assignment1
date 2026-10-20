"""Reject packages or versions outside the consumer's approved requirements."""
import argparse
from importlib import metadata
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APPROVAL_FILES = (
    "requirements.txt", "requirements-build.txt", "requirements-ci.txt",
    "ci/approved-local.txt",
)


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def load_approved(root=ROOT):
    approved = {}
    for filename in APPROVAL_FILES:
        for line in (root / filename).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)", line)
            if not match:
                raise ValueError(f"{filename}: exact name==version required: {line}")
            name, version = normalize(match[1]), match[2]
            if name in approved and approved[name] != version:
                raise ValueError(f"{filename}: conflicting approved version for {name}")
            approved[name] = version
    return approved


def compare(approved, installed):
    findings = []
    for name in sorted(installed.keys() - approved.keys()):
        findings.append(f"Unapproved package: {name}=={installed[name]}")
    for name in sorted(approved.keys() - installed.keys()):
        findings.append(f"Missing approved package: {name}=={approved[name]}")
    for name in sorted(approved.keys() & installed.keys()):
        if installed[name] != approved[name]:
            findings.append(f"Wrong version: {name}=={installed[name]}, expected {approved[name]}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        approved = load_approved()
        if args.validate_only:
            print(f"Approval files valid: {len(approved)} pinned packages.")
            return 0
        installed = {}
        duplicates = []
        for package in metadata.distributions():
            name = normalize(package.metadata["Name"])
            if name in installed:
                duplicates.append(f"Duplicate installed package: {name}")
            installed[name] = package.version
        findings = duplicates + compare(approved, installed)
        report = {"approved": approved, "installed": installed, "findings": findings}
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if findings:
            print("\n".join(findings))
            return 1
        print(f"Dependency approval passed: {len(installed)} installed packages.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Dependency approval failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
