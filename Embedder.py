import argparse
import json
import numpy as np
import faiss
import jsonlines
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class Embedder:
    def __init__(self, data="metadata.jsonl", faiss_out="faiss.index", embeddings_out="vectors.npy", model_name="all-MiniLM-L6-v2"):
        self.metadata = data
        self.faiss_out = faiss_out
        self.embeddings_out = embeddings_out
        self.model = SentenceTransformer(model_name)
        self.weights = {
            "title": 0.4,
            "summary": 0.1,
            "tags": 0.5
        }
    
    def load_metadata(self) -> List:
        # Parses metadata.json or metadata.jsonl and returns a list of note dictionaries
        with open(self.metadata, "r", encoding="utf8") as f:
            return [json.loads(line) for line in f]
        
    def embed_single_note(self, note : Dict, normalize_embeddings : bool) -> np.ndarray:
        tag_vecs = [self.model.encode(tag, normalize_embeddings=normalize_embeddings) for tag in note["tags"]]
        tag_vec = np.mean(tag_vecs, axis=0) if tag_vecs else np.zeros(self.model.get_sentence_embedding_dimension())
        title_vec = self.model.encode(note["title"], normalize_embeddings=True)
        summary_vec = self.model.encode(note["summary"], normalize_embeddings=True)
        return (self.weights["title"] * title_vec +
                self.weights["summary"] * summary_vec +
                self.weights["tags"] * tag_vec)
    
    def embed_notes(self, notes : List[Dict]) -> np.ndarray:
        embeddings = np.vstack([self.embed_single_note(n, normalize_embeddings=True) for n in notes])
        np.save(self.embeddings_out, embeddings)  
        return embeddings# e.g. vectors.npy
    
    def build_faiss_index(self):
        notes = self.load_metadata()
        embeddings = self.embed_notes(notes)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # inner-product (cosine if normalized)
        index.add(embeddings)
        faiss.write_index(index, self.faiss_out)
        print(f"Indexed {len(notes)} vectors into {self.faiss_out}")
    

    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="metadata.jsonl", help="metadata.json from extract")
    parser.add_argument("--index-out", default="faiss.index", help="where to write FAISS index")
    parser.add_argument("--embeddings-out", default="vectors.npy", help="where to save vectors.npy")
    args = parser.parse_args()

    embedder = Embedder(data=args.metadata, faiss_out=args.index_out, embeddings_out=args.embeddings_out)
    embedder.build_faiss_index()
    

if __name__ == "__main__":
    main()
