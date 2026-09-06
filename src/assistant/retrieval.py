import numpy as np
import pandas as pd
from typing import List, Dict, Any
import pickle
import os

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    from sklearn.metrics.pairwise import cosine_similarity

class FAISSRetriever:
    def __init__(self):
        self.index = None
        self.resolutions_df = pd.DataFrame()
        
    def build_index(self, resolutions_df: pd.DataFrame, embeddings: np.ndarray):
        self.resolutions_df = resolutions_df
        
        if len(embeddings) == 0:
            return
            
        if FAISS_AVAILABLE:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            faiss_embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
            self.index.add(faiss_embeddings)
        else:
            self.index = embeddings
            
    def retrieve(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.resolutions_df.empty or self.index is None:
            return []
            
        query = np.ascontiguousarray([query_embedding], dtype=np.float32)
        
        if FAISS_AVAILABLE:
            distances, indices = self.index.search(query, top_k)
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.resolutions_df) and idx != -1:
                    row_dict = self.resolutions_df.iloc[idx].to_dict()
                    row_dict['similarity_score'] = float(1.0 / (1.0 + distances[0][i]))
                    results.append(row_dict)
            return results
        else:
            sims = cosine_similarity(query, self.index)[0]
            top_indices = np.argsort(sims)[::-1][:top_k]
            results = []
            for idx in top_indices:
                row_dict = self.resolutions_df.iloc[idx].to_dict()
                row_dict['similarity_score'] = float(sims[idx])
                results.append(row_dict)
            return results
            
    def save_index(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            data = {
                'df': self.resolutions_df,
                'index_type': 'faiss' if FAISS_AVAILABLE else 'sklearn',
            }
            if FAISS_AVAILABLE and self.index is not None:
                data['faiss_index'] = faiss.serialize_index(self.index)
            else:
                data['embeddings'] = self.index
            pickle.dump(data, f)
            
    def load_index(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.resolutions_df = data['df']
            
            if data['index_type'] == 'faiss' and FAISS_AVAILABLE:
                self.index = faiss.deserialize_index(data['faiss_index'])
            else:
                self.index = data.get('embeddings', None)
