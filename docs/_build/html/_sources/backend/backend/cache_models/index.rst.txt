backend.cache_models
====================

.. py:module:: backend.cache_models

.. autoapi-nested-parse::

   Model Caching Script

   Caches local copies of embedding and reranker models so they can be loaded
   from disk at runtime (faster startup, no repeated network downloads).

   What it does
   ------------
   - For each ID in EMBEDDING_MODELS, downloads a SentenceTransformer and saves it
     under ./backend/cached_embedding_models/<sanitized_id>.
   - For each ID in RERANKER_MODELS, downloads a CrossEncoder reranker and saves it
     under ./backend/cached_reranker_models/<sanitized_id>.

   .. rubric:: Notes

   - `trust_remote_code=True` is enabled for SentenceTransformer to allow custom
     model code from the repository. Only use with sources you trust.
   - The imports `AutoTokenizer` and `AutoModel` from `transformers` are not used
     in this script and may be removed unless you rely on them elsewhere.



Attributes
----------

.. autoapisummary::

   backend.cache_models.EMBEDDING_MODELS
   backend.cache_models.RERANKER_MODELS
   backend.cache_models.EMBEDDINGS_DIR
   backend.cache_models.RERANKERS_DIR


Functions
---------

.. autoapisummary::

   backend.cache_models.sanitize_model_id
   backend.cache_models.cache_sentence_transformers
   backend.cache_models.cache_cross_encoders


Module Contents
---------------

.. py:data:: EMBEDDING_MODELS
   :value: ['IoannisKat1/multilingual-e5-large-legal-matryoshka',...


   List of embedding models to download

.. py:data:: RERANKER_MODELS
   :value: ['BAAI/bge-reranker-base']


   List of reranker models to download

.. py:data:: EMBEDDINGS_DIR

   Directory in which the embedding models will be cached for future use.

.. py:data:: RERANKERS_DIR

   Directory in which the reranker models will be cached for future use.

.. py:function:: sanitize_model_id(model_id: str) -> str

   Convert a model ID to a filesystem-friendly name.

   :param model_id: The model repository ID (e.g., "owner/name").
   :type model_id: str

   :returns: A sanitized string with slashes replaced by double underscores.
   :rtype: str


.. py:function:: cache_sentence_transformers(model_ids: Iterable[str], output_dir: pathlib.Path, *, trust_remote_code: bool = True) -> None

   Download and persist SentenceTransformer models to disk.

   :param model_ids: List/iterable of SentenceTransformer model IDs to cache.
   :type model_ids: Iterable[str]
   :param output_dir: Directory where models will be saved (one subfolder per model ID).
   :type output_dir: Path
   :param trust_remote_code: Whether to trust and execute custom modeling code from the repository.
                             Default is True. Use with caution for untrusted sources.
   :type trust_remote_code: bool, optional

   .. rubric:: Notes

   - Creates directories under `output_dir`.
   - Writes model weights/configuration to disk.


.. py:function:: cache_cross_encoders(model_ids: Iterable[str], output_dir: pathlib.Path) -> None

   Download and persist CrossEncoder reranker models to disk.

   :param model_ids: List/iterable of CrossEncoder model IDs to cache.
   :type model_ids: Iterable[str]
   :param output_dir: Directory where reranker models will be saved.
   :type output_dir: Path

   .. rubric:: Notes

   - Creates directories under `output_dir`.
   - Writes model weights/configuration to disk.


