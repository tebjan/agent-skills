#!/usr/bin/env python3
"""
Scan and repair lone Unicode surrogates in Claude Code JSONL chat files.

Lone surrogates (U+D800-U+DFFF) in stored JSON cause "invalid high surrogate"
errors when the Anthropic API rejects the request body. This script finds and
replaces them with U+FFFD (Unicode replacement character).

Usage:
    python fix_surrogates.py <path-to-jsonl-or-directory> [--dry-run] [--recursive]

Arguments:
    path        Path to a .jsonl file, a session directory, or the
                ~/.claude/projects/ root directory.
    --dry-run   Report what would be fixed without modifying files.
    --recursive Scan all .jsonl files under the given directory tree.
    --verbose   Show per-line details for each surrogate found.

Exit codes:
    0  All clean or all fixes applied successfully.
    1  Surrogates found (dry-run mode) or an error occurred.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def has_surrogates(s: str) -> bool:
    """Check if a string contains any lone surrogate code points."""
    return any(0xD800 <= ord(c) <= 0xDFFF for c in s)


def sanitize_string(s: str) -> str:
    """Replace lone surrogates with U+FFFD via encode/decode roundtrip."""
    if not isinstance(s, str):
        return s
    if not has_surrogates(s):
        return s
    return s.encode("utf-8", "surrogatepass").decode("utf-8", "replace")


def sanitize_obj(obj):
    """Recursively sanitize all strings in a parsed JSON object."""
    if isinstance(obj, str):
        return sanitize_string(obj)
    elif isinstance(obj, dict):
        return {sanitize_string(k): sanitize_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_obj(item) for item in obj]
    return obj


def scan_file(filepath: Path, dry_run: bool, verbose: bool) -> dict:
    """Scan a single file for lone surrogates. Returns a result dict."""
    result = {"path": str(filepath), "lines_total": 0, "lines_fixed": 0, "errors": []}

    try:
        with open(filepath, "r", encoding="utf-8", errors="surrogateescape") as f:
            lines = f.readlines()
    except Exception as e:
        result["errors"].append(f"Read error: {e}")
        return result

    result["lines_total"] = len(lines)
    fixed_lines = []
    any_fixed = False

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n").rstrip("\r")
        if not stripped:
            fixed_lines.append(line)
            continue

        # Check raw line for surrogates before JSON parsing
        raw_has_surrogate = has_surrogates(stripped)
        if raw_has_surrogate:
            stripped = sanitize_string(stripped)

        try:
            obj = json.loads(stripped)
            new_obj = sanitize_obj(obj)

            if new_obj != obj or raw_has_surrogate:
                result["lines_fixed"] += 1
                any_fixed = True
                new_line = json.dumps(new_obj, ensure_ascii=False, separators=(",", ":"))
                fixed_lines.append(new_line + "\n")
                if verbose:
                    print(f"  Line {i+1}: fixed surrogate(s)")
            else:
                fixed_lines.append(line)
        except json.JSONDecodeError as e:
            # Try to fix raw text if JSON parsing fails due to surrogates
            if raw_has_surrogate:
                fixed_lines.append(sanitize_string(line))
                result["lines_fixed"] += 1
                any_fixed = True
                if verbose:
                    print(f"  Line {i+1}: fixed raw (JSON parse failed: {e})")
            else:
                result["errors"].append(f"Line {i+1}: JSON parse error: {e}")
                fixed_lines.append(line)

    if any_fixed and not dry_run:
        backup = str(filepath) + ".bak"
        shutil.copy2(filepath, backup)
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        result["backup"] = backup

    return result


def scan_text_file(filepath: Path, dry_run: bool, verbose: bool) -> dict:
    """Scan a plain text file (not JSONL) for lone surrogates."""
    result = {"path": str(filepath), "lines_total": 0, "lines_fixed": 0, "errors": []}

    try:
        with open(filepath, "r", encoding="utf-8", errors="surrogateescape") as f:
            content = f.read()
    except Exception as e:
        result["errors"].append(f"Read error: {e}")
        return result

    result["lines_total"] = content.count("\n") + 1

    if has_surrogates(content):
        fixed = sanitize_string(content)
        result["lines_fixed"] = 1  # report as 1 fix for the whole file
        if not dry_run:
            backup = str(filepath) + ".bak"
            shutil.copy2(filepath, backup)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed)
            result["backup"] = backup
        if verbose:
            print(f"  Fixed surrogate(s) in text file")

    return result


def find_session_files(session_path: Path) -> list[Path]:
    """Find all scannable files for a session (JSONL + subagents + tool-results)."""
    files = []

    # Main JSONL
    jsonl = session_path.with_suffix(".jsonl")
    if jsonl.exists():
        files.append(jsonl)

    # Session directory (subagents, tool-results)
    session_dir = session_path if session_path.is_dir() else session_path.with_suffix("")
    if session_dir.is_dir():
        for f in session_dir.rglob("*.jsonl"):
            if f not in files:
                files.append(f)
        for f in session_dir.rglob("*.txt"):
            files.append(f)
        for f in session_dir.rglob("*.json"):
            files.append(f)

    return files


def main():
    parser = argparse.ArgumentParser(
        description="Scan and repair lone Unicode surrogates in Claude Code JSONL files."
    )
    parser.add_argument("path", help="Path to .jsonl file, session dir, or projects root")
    parser.add_argument("--dry-run", action="store_true", help="Report without modifying")
    parser.add_argument("--recursive", action="store_true", help="Scan all .jsonl files recursively")
    parser.add_argument("--verbose", action="store_true", help="Show per-line details")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    all_results = []

    if target.suffix == ".jsonl" and target.is_file():
        # Single JSONL file — also scan its session directory
        print(f"Scanning session: {target.name}")
        files = find_session_files(target)
        for f in files:
            print(f"  Scanning: {f.name}")
            if f.suffix == ".jsonl":
                result = scan_file(f, args.dry_run, args.verbose)
            else:
                result = scan_text_file(f, args.dry_run, args.verbose)
            all_results.append(result)

    elif target.is_dir():
        if args.recursive:
            jsonl_files = sorted(target.rglob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
        else:
            jsonl_files = sorted(target.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)

        print(f"Scanning {len(jsonl_files)} JSONL files in {target}")
        for f in jsonl_files:
            result = scan_file(f, args.dry_run, args.verbose)
            all_results.append(result)
            if result["lines_fixed"] > 0:
                print(f"  {f.name}: {result['lines_fixed']} lines fixed")
    else:
        print(f"Error: {target} is not a file or directory", file=sys.stderr)
        sys.exit(1)

    # Summary
    total_files = len(all_results)
    files_with_fixes = sum(1 for r in all_results if r["lines_fixed"] > 0)
    total_fixes = sum(r["lines_fixed"] for r in all_results)
    total_errors = sum(len(r["errors"]) for r in all_results)

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Summary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Files with surrogates: {files_with_fixes}")
    print(f"  Total lines/sections fixed: {total_fixes}")
    if total_errors:
        print(f"  Errors: {total_errors}")
        for r in all_results:
            for e in r["errors"]:
                print(f"    {r['path']}: {e}")

    if files_with_fixes > 0:
        if args.dry_run:
            print("\nRun without --dry-run to apply fixes.")
            sys.exit(1)
        else:
            print("\nBackups saved with .bak extension.")
    else:
        print("\nAll files clean — no surrogates found.")

    sys.exit(0)


if __name__ == "__main__":
    main()
