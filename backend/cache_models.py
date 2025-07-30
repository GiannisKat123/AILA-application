from transformers import AutoTokenizer, AutoModel
from sentence_transformers import CrossEncoder
from sentence_transformers import SentenceTransformer

EMBEDDING_MODELS = [
    "IoannisKat1/multilingual-e5-large-legal-matryoshka",
    "IoannisKat1/modernbert-embed-base-legal-matryoshka-2",
    "IoannisKat1/bge-m3-legal-matryoshka",
    "IoannisKat1/legal-bert-base-uncased-legal-matryoshka"
]

RERANKER_MODELS = [
    'BAAI/bge-reranker-base'
]

for model_id in EMBEDDING_MODELS:
    print(f"📦 Caching sentence-transformers model: {model_id}")
    save_path = f"./backend/cached_embedding_models/{model_id.replace('/', '__')}"
    model = SentenceTransformer(model_id, trust_remote_code=True)
    model.save(save_path)

# Cache CrossEncoder models
for model_id in RERANKER_MODELS:
    print(f"🔁 Caching reranker: {model_id}")
    reranker = CrossEncoder(model_id)
    reranker.save(f"./backend/cached_reranker_models/{model_id.replace('/', '__')}")