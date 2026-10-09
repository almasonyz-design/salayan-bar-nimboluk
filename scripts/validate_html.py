#!/usr/bin/env python3
"""Lightweight release checks for the single-file Salayan Bar web app."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.ids = []
        self.inline_scripts = []
        self._script_attrs = None
        self._script_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag.lower() == "script":
            self._script_attrs = attrs
            self._script_parts = []

    def handle_data(self, data):
        if self._script_attrs is not None and "src" not in self._script_attrs:
            self._script_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._script_attrs is not None:
            attrs = self._script_attrs
            script = "".join(self._script_parts)
            script_type = (attrs.get("type") or "").lower()
            if "src" not in attrs and script.strip() and script_type not in ("application/json", "application/ld+json", "importmap"):
                self.inline_scripts.append((attrs.get("id", "inline-script"), script))
            self._script_attrs = None
            self._script_parts = []

def main():
    if not HTML.exists():
        print("FAIL: index.html not found")
        return 1
    source = HTML.read_text(encoding="utf-8")
    parser = AuditParser()
    parser.feed(source)
    parser.close()
    failures = []

    if "<!doctype html>" not in source[:300].lower():
        failures.append("Missing HTML5 doctype.")
    if "<html" not in source.lower() or "</html>" not in source.lower():
        failures.append("Missing opening or closing html tag.")
    if not parser.inline_scripts:
        failures.append("No inline JavaScript found to check.")

    counts = Counter(parser.ids)
    duplicates = sorted(k for k, v in counts.items() if k and v > 1)
    if duplicates:
        failures.append("Duplicate static HTML IDs: " + ", ".join(duplicates))

    checked = 0
    with tempfile.TemporaryDirectory(prefix="salayan-qa-") as temp:
        for index, (name, script) in enumerate(parser.inline_scripts, start=1):
            path = Path(temp) / f"inline-{index}.js"
            path.write_text(script, encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(path)],
                text=True, capture_output=True
            )
            checked += 1
            if result.returncode:
                error_lines = (result.stderr or result.stdout).strip().splitlines()
                detail = " | ".join(error_lines[:4]) if error_lines else "unknown syntax error"
                failures.append(f"JavaScript syntax error in {name}: {detail}")

    if failures:
        print("SALAYAN BAR RELEASE CHECKS: FAILED")
        for failure in failures:
            print(" - " + failure)
        return 1

    print("SALAYAN BAR RELEASE CHECKS: PASSED")
    print(f" - HTML source: {len(source):,} characters")
    print(f" - Unique static IDs: {len(counts)}")
    print(f" - Inline JavaScript blocks syntax-checked: {checked}")
    print(" - Note: external APIs, Supabase policies, authentication and real-device GPS still require live integration tests.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
