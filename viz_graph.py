#!/usr/bin/env python3
import json
import argparse
import networkx as nx
import matplotlib.pyplot as plt

def load_graph(path):
    with open(path, encoding='utf8') as f:
        data = json.load(f)
    G = nx.DiGraph()  # or Graph() if you want undirected
    for node, nbrs in data.items():
        G.add_node(node)
        for edge in nbrs:
            target = edge['id']
            weight = edge.get('score', 1.0)
            G.add_edge(node, target, weight=weight)
    return G

def draw_graph(G, top_n=50, min_weight=0.25):
    # Optionally prune: only keep top_n nodes by degree or drop low-weight edges
    # Example: remove edges below threshold
    to_remove = [
        (u,v) for u,v,d in G.edges(data=True)
        if d['weight'] < min_weight
    ]
    G.remove_edges_from(to_remove)

    # If it’s too big, you can take the subgraph of the top_n highest-degree nodes
    if G.number_of_nodes() > top_n:
        deg = dict(G.degree())
        top_nodes = sorted(deg, key=deg.get, reverse=True)[:top_n]
        G = G.subgraph(top_nodes).copy()

    # Layout and draw
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    plt.figure(figsize=(12,12))
    # draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, alpha=0.8)
    # draw edges with alpha proportional to weight
    weights = [d['weight'] for _,_,d in G.edges(data=True)]
    nx.draw_networkx_edges(
        G, pos,
        width=[w * 2 for w in weights],
        alpha=0.6,
        arrowstyle='-|>',
        arrowsize=10
    )
    # labels
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.axis('off')
    plt.title("Obsidian Vault Semantic Graph")
    plt.tight_layout()
    plt.show()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--graph", default="graph.json", help="Path to graph.json")
    p.add_argument("--top-n",   type=int,   default=75,   help="Max number of nodes to show")
    p.add_argument("--min-wt",  type=float, default=0.25, help="Drop edges below this similarity")
    args = p.parse_args()

    G = load_graph(args.graph)
    draw_graph(G, top_n=args.top_n, min_weight=args.min_wt)

if __name__ == "__main__":
    main()
