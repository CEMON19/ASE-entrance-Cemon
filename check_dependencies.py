#!/usr/bin/env python3
"""Check a requirements.txt (name==version lines) against PyPI for Python 3.11."""
import json
import sys
import urllib.error
import urllib.request

from packaging.specifiers import SpecifierSet
from packaging.version import Version

TARGET = Version("3.11")


def fetch_release(name, version):
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def min_python(spec):
    """Highest lower bound among the specifier clauses (minimum Python version)."""
    best = Version("0")
    for s in spec:
        if s.operator in (">=", ">", "==", "~=", "==="):
            v = Version(s.version.replace(".*", ""))
            if v > best:
                best = v
    return best


def main(path):
    lines = [l.strip() for l in open(path) if l.strip() and not l.strip().startswith("#")]
    not_found = incompatible = 0
    highest = None  # (min_version, name, version)
    for line in lines:
        name, _, version = line.partition("==")
        name, version = name.strip(), version.strip()
        data = fetch_release(name, version)
        if data is None:
            not_found += 1
            continue
        rp = (data["info"].get("requires_python") or "").strip()
        if not rp:
            continue  # counts as compatible
        spec = SpecifierSet(rp)
        if not spec.contains(TARGET, prereleases=True):
            incompatible += 1
        m = min_python(spec)
        if highest is None or m > highest[0]:
            highest = (m, name, version)
    print(f"Dependencies checked: {len(lines)}")
    print(f"Not found on PyPI: {not_found}")
    print(f"Incompatible with Python 3.11: {incompatible}")
    if highest:
        m, n, v = highest
        print(f"Highest requirement: {n}=={v} (>={m})")
    else:
        print("Highest requirement: none")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "requirements.txt")