#!/usr/bin/env python3
import argparse
import json
import os
import re
import yaml

class Injector:
    FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def __init__(self, vault: str, graph: str):
        self.vault = vault
        self.graph = graph

    def inject(path: str, related_ids):
        text = open(path, encoding="utf8").read()
        m = self.FRONT_MATTER_RE.match(text)
        if not m:
            # no front-matter: prepend one
            fm = {"related": related_ids}
            body = text
        else:
            fm = yaml.safe_load(m.group(1)) or {}
            fm["related"] = related_ids
            body = text[m.end():]

        new_fm = "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n"
        with open(path, "w", encoding="utf8") as f:
            f.write(new_fm + body)

    def inject_all(self):
        graph = json.load(open(self.graph, encoding="utf8"))
        for note_id, neighbors in graph.items():
            path = os.path.join(self.vault, note_id)
            related = [n["id"] for n in neighbors]
            self.inject(path, related)
        print(f"Injected related links into {len(graph)} notes")
        

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--graph",   default="generations/graph.json", help="path to the graph file")
    p.add_argument("--vault",   default="example_vault", help="path to your vault folder")
    injector = Injector(
        vault=p.parse_args().vault,
        graph=p.parse_args().graph
    )
    injector.inject_all()

if __name__ == "__main__":
    main()
