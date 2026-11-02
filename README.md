# ASE-entrance-Cemon

# Python 3.11 Dependency Checker

A small script that checks every line of a `requirements.txt` against PyPI **before** you run `pip install`, and reports which lines will fail on **Python 3.11**.

It is useful for requirements files written by AI coding agents, which often pin versions that don't exist or packages that were never published.

## What it reports

| Output | Meaning |
|---|---|
| **Dependencies checked** | Number of lines in the file |
| **Not found on PyPI** | The package doesn't exist, or the pinned version doesn't |
| **Incompatible with Python 3.11** | The release exists, but its `requires_python` excludes 3.11 (upper bounds such as `<3.10` are checked too) |
| **Highest requirement** | Among existing releases that declare `requires_python`, the one with the highest minimum Python version, printed as `name==version (>=3.x)` |

A release with no `requires_python` counts as compatible.

## Requirements

- Python 3.8 or newer to run the script
- The `packaging` library
- Internet access to `pypi.org`

```bash
pip install packaging
```

The check always targets Python 3.11, regardless of which Python version runs the script.

## Usage

```bash
python check_deps.py requirements.txt
```

If no file is given, it defaults to `requirements.txt` in the current folder.

### Input format

One pinned dependency per line, in the form `name==version`. Blank lines and `#` comments are ignored.

```
django==4.2
numpy==2.3.0
scipy==1.7.0
scikit-learn==1.4.0
fastapi-agent-router==0.3.1
matplotlib==3.99.0
six==1.16.0
requests==2.32.0
```

### Output

```
Dependencies checked: 8
Not found on PyPI: 2
Incompatible with Python 3.11: 1
Highest requirement: numpy==2.3.0 (>=3.11)
```

Here `fastapi-agent-router` doesn't exist, `matplotlib==3.99.0` is a nonexistent version, and `scipy==1.7.0` is capped below Python 3.10.

## How it works

1. For each line, it requests `https://pypi.org/pypi/<name>/<version>/json` from the [PyPI JSON API](https://docs.pypi.org/api/json).
2. A 404 response counts as "not found". This covers both a missing package and a missing version.
3. Otherwise it reads `info.requires_python` and tests it against 3.11 with `packaging.specifiers.SpecifierSet`.
4. It finds each release's minimum Python version (the highest lower bound in its specifier) and keeps the largest.

Only `urllib` and `json` from the standard library are used for networking, and `packaging` handles all version logic.
