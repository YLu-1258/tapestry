# TAPESTRY: Obsidian Semantic Vault Toolkit

A set of Python scripts to:
1. Generate a sample Obsidian vault with AI‐enriched notes (generate_test_vault.py)
2. Extract YAML metadata (tags, titles, summaries) from a vault (Extractor.py).
3. Build a FAISS vector index of note embeddings (Embedder.py).
4. Find semantic neighbors between notes (GraphBuilder.py).
5. Visualize the resulting note graph (viz_graph.py).

# 📦 Installation

## Clone this repository
```
git clone https://github.com/YLu-1258/tapestry.git
cd tapestry
```
## Create a virtual environment (recommended)
```
python3 -m venv venv
source venv/bin/activate
```
## Install dependencies

`pip install -r requirements.txt`

requirements.txt should include:
```
faiss-cpu
jsonlines
mistralai
numpy
PyYAML
sentence_transformers
matplotlib
networkx
```

# 🔧 Script Overview & Usage

**1. Generate a Test Vault**
```
python generate_test_vault.py \
  --vault ./test_vault \
  --notes 75 \
  --max-tags 5
```
Creates a folder (`./test_vault`) with random subfolders and Markdown notes.
Each note is enriched by Mistral AI, producing a title and short paragraph based on randomly chosen tags.

Note: Set your Mistral API key in `~/.zshrc`:
```
export MISTRAL_API_KEY="your_api_key_here"
```
**2. Extract Note Metadata**
```
python main/Extractor.py \
  --vault ./test_vault \
  --out generations/metadata.jsonl
```

Parses YAML front-matter from each .md file and writes a JSON list of notes:
```json
[
  {"id": "note_1.md", "path": "./test_vault/note_1.md", "tags": [...], "title": "...", "summary": "..."},
  ...
]
```
**3. Build FAISS Index**
```
python main/Embedder.py \
  --metadata generations/metadata.jsonl \
  --embeddings-out generations/vectors.npy \
  --index-out   generations/faiss.index
```
Combines tags + summaries into text, embeds with a sentence-transformer model (e.g. all-MiniLM-L6-v2), stores vectors in vectors.npy, and writes a FAISS index for similarity search.

**4. Find Semantic Neighbors**
```
python main/GraphBuilder.py \
  --metadata generations/metadata.jsonl \
  --embeddings generations/vectors.npy \
  --index generations/faiss.index \
  --k 5 --threshold 0.4 \
  --out generations/graph.json
```
Searches each note vector for its top‑k neighbors above a similarity threshold, producing a JSON adjacency list:
```json
{
  "note_1.md": [ {"id": "note_5.md", "score": 0.87}, ... ],
  ...
}
```
**5. Inject Related Links (Not yet released)**
```
python main/Injector.py \
  --graph generations/graph.json \
  --vault ./test_vault
```
Updates each Markdown file’s front-matter to include:

related:
  - note_5.md
  - note_2.md
  ...

so Obsidian will display backlinks automatically.

**6. Visualize the Graph**
```
python viz_graph.py \
  --graph generations/graph.json \
  --top-n 75 \
  --min-wt 0.25
```
Loads graph.json into a NetworkX graph, prunes low‑weight edges, optionally limits to the top‑N nodes by degree, and draws a force‑directed layout via Matplotlib.

# ⚙️ Configuration & Customization

Tag weighting: adjust how tags vs. content are embedded in build_index.py.

AI prompt: refine the Mistral prompt in generate_test_vault.py for different styles.

Index parameters: swap FAISS index types (e.g. IndexHNSWFlat for large-scale).

Visualization layout: tweak spring_layout parameters in viz_graph.py (e.g., k, iterations).

# 📄 License

This project is licensed under the MIT License. See LICENSE for details.

Happy knowledge‑weaving!

