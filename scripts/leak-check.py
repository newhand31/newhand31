"""Fail-closed leak gate (copied from public-brain).

Scans text files against two rule files:
  rules/leak-rules.json   generic, non-identifying patterns (tracked, public-safe)
  <private rules>         identifying patterns; never stored in this repo

Private rules path: env BRAIN_LEAK_RULES, else `git config brain.leakRules` (kept in .git/config,
never in a tracked file). If the private file is missing the gate refuses to run
(exit 2) unless --allow-missing-private is passed explicitly: a half-blind gate that
reports "clean" is worse than no gate.

Default scope: paths staged for commit (content read from the working tree).
--all scans every tracked text file. Explicit paths override both.

Exit codes: 0 clean, 1 leaks found, 2 gate could not run.
Output names file, line and rule only. It never echoes the matched text.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

TEXT_EXT = {".md", ".txt", ".html", ".css", ".psm1", ".psd1", ".json", ".yml", ".yaml", ".csv", ".canvas",
            ".py", ".ps1", ".sh", ".js", ".mjs", ".ts", ".toml", ".ini"}
SKIP_PREFIXES = ("rules/",)  # rule files describe patterns; they are not content


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))


def load_rules(path, label):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    rules = []
    for rule in data.get("rules", []):
        rules.append((label + ":" + rule["name"], re.compile(rule["pattern"], re.IGNORECASE)))
    return rules


def git_paths(root, *args):
    out = subprocess.run(["git", *args, "-z"], cwd=root, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="scan every tracked text file instead of staged paths")
    parser.add_argument("--allow-missing-private", action="store_true",
                        help="run with generic rules only when the private rules file is absent (explicit opt-in)")
    parser.add_argument("paths", nargs="*", help="explicit files to scan (overrides --all and staged)")
    args = parser.parse_args()

    root = repo_root()
    generic_path = os.path.join(root, "rules", "leak-rules.json")
    private_path = os.environ.get("BRAIN_LEAK_RULES") or subprocess.run(
        ["git", "config", "--get", "brain.leakRules"], cwd=root, capture_output=True, text=True).stdout.strip()

    rules = load_rules(generic_path, "generic")
    if os.path.isfile(private_path):
        rules += load_rules(private_path, "private")
    elif args.allow_missing_private:
        print("leak-check: WARNING private rules missing; running generic rules only", file=sys.stderr)
    else:
        print("leak-check: private rules file not found. Set BRAIN_LEAK_RULES or `git config brain.leakRules <path>`. "
              "Refusing to run half-blind (exit 2).", file=sys.stderr)
        return 2

    if args.paths:
        files = args.paths
    elif args.all:
        files = git_paths(root, "ls-files")
    else:
        files = git_paths(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")

    hits = 0
    scanned = 0
    for rel in files:
        norm = rel.replace(os.sep, "/")
        if norm.startswith(SKIP_PREFIXES):
            continue
        if os.path.splitext(norm)[1].lower() not in TEXT_EXT:
            continue
        for name, pattern in rules:
            if pattern.search(norm):
                print(norm + ": filename matches " + name)
                hits += 1
        path = rel if os.path.isabs(rel) else os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        scanned += 1
        with open(path, encoding="utf-8", errors="replace") as handle:
            for lineno, line in enumerate(handle, 1):
                for name, pattern in rules:
                    if pattern.search(line):
                        print(norm + ":" + str(lineno) + ": " + name)
                        hits += 1

    if hits:
        print("leak-check: " + str(hits) + " hit(s) in " + str(scanned) + " file(s). Commit refused.", file=sys.stderr)
        return 1
    print("leak-check: clean (" + str(scanned) + " file(s), " + str(len(rules)) + " rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
