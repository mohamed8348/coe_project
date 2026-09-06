import re
import numpy as np
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    from sklearn.feature_extraction.text import TfidfVectorizer

class FeatureExtractor:
    def __init__(self):
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = TfidfVectorizer(max_features=384)
            self.is_fit = False
            
    def extract(self, bug_dict: Dict[str, Any]) -> np.ndarray:
        text = f"{bug_dict.get('title', '')} {bug_dict.get('description', '')} {bug_dict.get('log_content_clean', '')}"
        text = text[:2000] # Truncate to approx 512 tokens
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            return self.model.encode([text])[0]
        else:
            if not self.is_fit:
                self.model.fit([text])
                self.is_fit = True
            vector = self.model.transform([text]).toarray()[0]
            return vector
            
    def extract_log_keywords(self, log_content: str) -> List[str]:
        keywords = []
        if not log_content:
            return keywords
            
        exceptions = re.findall(r'\b[A-Z][a-zA-Z]*Exception\b', log_content)
        error_codes = re.findall(r'\bERR-\d+\b|\bHTTP \d{3}\b', log_content)
        
        keywords.extend(exceptions)
        keywords.extend(error_codes)
        return list(set(keywords))
        
    def extract_screenshot_features(self, screenshot_meta: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            'has_error_dialog': screenshot_meta.get('has_error_dialog', False),
            'button_states': screenshot_meta.get('button_states', {}),
            'text_extracted': screenshot_meta.get('text_extracted', '')
        }
        return normalized
