import faiss
import numpy as np
import pandas as pd
from typing import List, Dict
from app.services.embed import embed_texts

class Retriever:
    def __init__(self):
        self.index = None
        self.meta = None

    def build(self, df: pd.DataFrame):
        vecs = embed_texts(df["chunk_text"].tolist())
        faiss.normalize_L2(vecs)
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)
        self.meta = df.reset_index(drop=True)

    def search(self, query: str, k: int = 5) -> List[Dict]:
        q = embed_texts([query]).astype("float32")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            row = self.meta.iloc[int(idx)].to_dict()
            row["score"] = float(score)
            hits.append(row)
        return hits

