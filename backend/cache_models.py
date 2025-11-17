from pathlib import Path
from typing import Iterable
from sentence_transformers import CrossEncoder, SentenceTransformer

EMBEDDING_MODELS = [
    "IoannisKat1/multilingual-e5-large-legal-matryoshka",
    "IoannisKat1/modernbert-embed-base-legal-matryoshka-2",
    "IoannisKat1/bge-m3-legal-matryoshka",
    "IoannisKat1/legal-bert-base-uncased-legal-matryoshka",
]

RERANKER_MODELS = [
    "BAAI/bge-reranker-base",
    "IoannisKat1/bge-reranker-basefinetuned-new"
]

EMBEDDINGS_DIR = Path("./backend/cached_embedding_models")
"""Directory in which the embedding models will be cached for future use."""
RERANKERS_DIR = Path("./backend/cached_reranker_models")
"""Directory in which the reranker models will be cached for future use."""

def sanitize_model_id(model_id:str) -> str:
    return model_id.replace('/','__')

def cache_sentence_transformers(model_ids:Iterable[str],output_dir:Path,*,trust_remote_code:bool=True):
    output_dir.mkdir(parents=True,exist_ok=True)
    for model_id in model_ids:
        print(f"📦 Caching sentence-transformers model: {model_id}")
        save_path = output_dir/sanitize_model_id(model_id)
        model = SentenceTransformer(model_id,trust_remote_code)
        model.save(str(save_path))

def cache_cross_encoders(model_ids:Iterable[str],output_dir:Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for model_id in model_ids:
        print(f"🔁 Caching reranker: {model_id}")
        save_path = output_dir / sanitize_model_id(model_id)
        reranker = CrossEncoder(model_id)
        reranker.save(str(save_path))

if __name__  == '__main__':
    cache_cross_encoders(RERANKER_MODELS,RERANKERS_DIR)
    cache_sentence_transformers(EMBEDDING_MODELS,EMBEDDINGS_DIR,trust_remote_code=True)
    