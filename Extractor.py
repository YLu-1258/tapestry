#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import List, Dict

import yaml

class Extractor:
    FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def __init__(self, vault_dir: str, output_file: str = "metadata.jsonl"):
        self.vault_dir = vault_dir
        self.output_file = output_file

    def parse_front_matter(self, text: str) -> Dict:
        m = self.FRONT_MATTER_RE.match(text)
        if not m:
            return {}
        return yaml.safe_load(m.group(1)) or {}

    def extract_summary(self, body: str) -> str:
        # first non-empty paragraph
        for para in body.split("\n\n"):
            if para.strip():
                return para.strip().replace("\n", " ")
        return ""

    def scan_notes(self, vault_dir: str) -> int:
        notes_scanned = 0
        with open(self.output_file, "w", encoding="utf8") as f:
            for root, _, files in os.walk(vault_dir):
                for fn in files:
                    if not fn.endswith(".md"):
                        continue
                    path = os.path.join(root, fn)
                    text = open(path, encoding="utf8").read()
                    fm = self.parse_front_matter(text)
                    body = self.FRONT_MATTER_RE.sub("", text)
                    note = {
                        "id": os.path.relpath(path, vault_dir),
                        "path": path,
                        "tags": fm.get("tags", []),
                        "title": fm.get("title", ""),
                        "summary": self.extract_summary(body),
                    }
                    f.write(json.dumps(note, ensure_ascii=False) + "\n")
                    notes_scanned += 1
        return notes_scanned


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vault", required=True, help="path to your vault folder")
    p.add_argument("--out", required=True, help="metadata.json output path")
    args = p.parse_args()
    extractor = Extractor(args.vault, args.out)
    notes = extractor.scan_notes(args.vault)
    print(f"Wrote {len(notes)} notes to {args.out}")

if __name__ == "__main__":
    main()
