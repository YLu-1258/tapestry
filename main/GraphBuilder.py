#!/usr/bin/env python3
import argparse
import json
import numpy as np
import faiss
from typing import List

class GraphBuilder:
    def __init__(self, metadata_file: str, embeddings_file: str, index_file: str, k: int = 5, threshold: float = 0.2, out_file: str = "graph.json"):
        self.notes = self.load_metadata(metadata_file)
        self.vectors = np.load(embeddings_file)
        self.index = faiss.read_index(index_file)
        self.k = k
        self.threshold = threshold
        self.out_file = out_file

    def load_metadata(self, metadata_file : str) -> List:
        # Parses metadata.json or metadata.jsonl and returns a list of note dictionaries
        with open(metadata_file, "r", encoding="utf8") as f:
            return [json.loads(line) for line in f]
    
    def build_graph(self):
        sims, idxs = self.index.search(self.vectors, self.k + 1)
        graph = {}
        for i, note in enumerate(self.notes):
            neighbors = []
            for score, j in zip(sims[i], idxs[i]): 
                if score >= self.threshold and note["id"] != self.notes[j]["id"]:
                    neighbors.append({"id": self.notes[j]["id"], "score": float(score)})
            graph[note["id"]] = neighbors
        
        with open(self.out_file, "w", encoding="utf8") as f:
            json.dump(graph, f, indent=2)
        print(f"Wrote graph with {len(graph)} nodes to {self.out_file}")
    
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", default="generations/metadata.jsonl", help="metadata.json from extract")
    p.add_argument("--embeddings", default="generations/vectors.npy", help="vectors.npy from embed")
    p.add_argument("--index", default="generations/faiss.index", help="FAISS index file")
    p.add_argument("--k",      type=int, default=5)
    p.add_argument("--threshold", type=float, default=0.4)
    p.add_argument("--out",    default="generations/graph.json", help="output graph file")

    builder = GraphBuilder(
        metadata_file=p.parse_args().metadata,
        embeddings_file=p.parse_args().embeddings,
        index_file=p.parse_args().index,
        k=p.parse_args().k,
        threshold=p.parse_args().threshold,
        out_file=p.parse_args().out
    )

    builder.build_graph()

if __name__ == "__main__":
    main()
