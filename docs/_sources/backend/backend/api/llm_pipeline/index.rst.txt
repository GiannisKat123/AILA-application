backend.api.llm_pipeline
========================

.. py:module:: backend.api.llm_pipeline

.. autoapi-nested-parse::

   LLM Pipeline Orchestration

   This module defines:
   - Utilities for loading vector indexes and reranker models
   - A TypedDict AgentState for LangGraph workflows
   - LLM_Pipeline: a LangGraph-based workflow for legal question answering

   Key Components
   --------------
   1. load_vector_index(top_k, persist_dir, embedding)
      -> Loads a LlamaIndex vector index with a given embedding model and returns a retriever.

   2. load_reranker_model()
      -> Loads a Cohere client + finetuned reranker model.

   3. initialize_indexes(top_k)
      -> Preloads all vector indexes (Phishing, Law Cases Recall/Precision,      Greek Penal Code Recall/Precision, GDPR Recall/Precision).

   4. AgentState
      -> TypedDict describing the state used across LangGraph workflow.

   5. LLM_Pipeline
      -> Orchestrates the RAG pipeline:

           - starting_prompt: safety & relevance check
           - query_translation: ensure English queries for retrieval
           - query_rewriting: generate paraphrases for broader coverage
           - run_classifications_parallel: classify into multiple categories
           - run_retrievals_parallel: retrieve from multiple indexes
           - get_context: summarize retrieved docs
           - web_search: complementary retrieval from TavilySearch
           - run_full_pipeline: executes the full flow end-to-end



Classes
-------

.. autoapisummary::

   backend.api.llm_pipeline.AgentState
   backend.api.llm_pipeline.LLM_Pipeline


Functions
---------

.. autoapisummary::

   backend.api.llm_pipeline.load_vector_index
   backend.api.llm_pipeline.load_reranker_model
   backend.api.llm_pipeline.initialize_indexes


Module Contents
---------------

.. py:function:: load_vector_index(top_k: int, persist_dir: str, embedding)

   Load a LlamaIndex vector index with a specified embedding model.

   :param top_k: Max number of docs to retrieve.
   :type top_k: int
   :param persist_dir: Directory containing the persisted index.
   :type persist_dir: str
   :param embedding: Embedding model to use for retrieval.
   :type embedding: HuggingFaceEmbeddings

   :returns: A retriever configured for hybrid search with similarity top_k.
   :rtype: VectorIndexRetriever


.. py:function:: load_reranker_model()

   Load a Cohere client and finetuned reranker model.

   :returns: (Cohere client, finetuned model reference)
   :rtype: tuple


.. py:function:: initialize_indexes(top_k: int)

   Initialize and return all domain-specific retrievers.

   Domains:

   - Phishing

   - Law Cases (Recall & Precision)

   - Greek Penal Code (Recall & Precision)

   - GDPR (Recall & Precision)


   :rtype: dict[str, VectorIndexRetriever]


.. py:class:: AgentState

   Bases: :py:obj:`TypedDict`


   Shared state for the pipeline's LangGraph workflow.


   .. py:attribute:: user_query
      :type:  str


   .. py:attribute:: summarized_context
      :type:  str


   .. py:attribute:: search_results
      :type:  str


   .. py:attribute:: questions
      :type:  List[str]


   .. py:attribute:: query_classification
      :type:  Annotated[Dict[str, List[str]], operator.or_]


   .. py:attribute:: retrieved_docs
      :type:  Annotated[Dict[str, List], operator.or_]


   .. py:attribute:: context
      :type:  Annotated[Dict[str, str], operator.or_]


.. py:class:: LLM_Pipeline(index_mapping, reranker_model, cohere_client=None)

   LangGraph-based pipeline for multilingual, legal RAG.

   Steps
   -----
   1. starting_prompt: check if query is legal, safe, in-domain.
   2. query_translation: translate non-English queries to English.
   3. query_rewriting: produce paraphrases to improve recall.
   4. query_classification: assign categories (GDPR, GPC, Phishing, Cases).
   5. retrieving_docs: fetch from indexes, rerank with CrossEncoder or Cohere.
   6. get_context: summarize retrieved docs into coherent context.
   7. web_search: augment with TavilySearch.
   8. run_full_pipeline: execute all steps and return final structured response.

   .. attribute:: index_mapping

      Preloaded retrievers.

      :type: dict[str, VectorIndexRetriever]

   .. attribute:: reranker_model

      Model used to rerank retrieved documents.

      :type: CrossEncoder | GetFinetunedModelResponse

   .. attribute:: cohere_client

      Optional client for Cohere reranking.

      :type: cohere.ClientV2 | None

   .. attribute:: model

      LLM used for classification, rewriting, summarization.

      :type: ChatOpenAI


   .. py:attribute:: dict_lang

      Dictionary of languages to recognize


   .. py:attribute:: app

      Initializes the workflow of the RAG application


   .. py:method:: retrieving_docs(query: str, index_mapping: dict[str, llama_index.core.retrievers.VectorIndexRetriever], indexes: List[llama_index.core.retrievers.VectorIndexRetriever], reranker_model: sentence_transformers.CrossEncoder | cohere.finetuning.finetuning.types.get_finetuned_model_response.GetFinetunedModelResponse, cohere_client: cohere.client_v2.ClientV2 | None)

      Retrieve and rerank documents for a given query.

      :param query: The user query (in English, after translation).
      :type query: str
      :param index_mapping: Mapping of index keys to retrievers.
      :type index_mapping: dict[str, VectorIndexRetriever]
      :param indexes: Keys from index_mapping specifying which retrievers to query.
      :type indexes: list[str]
      :param reranker_model: Model used to rerank results. Supports SentenceTransformer CrossEncoder
                             or a Cohere finetuned model reference.
      :type reranker_model: CrossEncoder | GetFinetunedModelResponse
      :param cohere_client: Cohere client, required if reranker_model is Cohere.
      :type cohere_client: cohere.ClientV2 | None

      :returns: List of [doc_text, metadata, score] for top reranked documents.
      :rtype: list[list]



   .. py:method:: starting_prompt(query: str)

      Classify a query as legal, non-legal, or unsafe.

      :param query: The raw user query.
      :type query: str

      :returns: [bool, str | None] indicating if legal and optional message.
      :rtype: list

      .. rubric:: Notes

      - If legal: returns [True, None]
      - If non-legal: returns [False, "<short helpful answer + reminder>"]
      - If unsafe (medical, financial, illegal, etc.): returns
        [False, "I'm a legal assistant. I cannot answer unsafe..."]



   .. py:method:: query_translation(query: str)

      Translate query into English if necessary.

      :param query: User query in any supported language.
      :type query: str

      :returns: (language_name, translated_query)
      :rtype: tuple



   .. py:method:: web_search(query: str)

      Perform a web search via TavilySearch and summarize results.

      :param query: User query (in English).
      :type query: str

      :returns: {'search_results': str} summarizing retrieved context.
      :rtype: dict



   .. py:method:: rag_pipeline(query: str)

      Run the LangGraph workflow (query rewriting -> classification -> retrieval -> context).

      :param query: User query in English.
      :type query: str

      :returns: {'query': query,'summarized_context': str}
      :rtype: dict



   .. py:method:: query_rewriting(state)

      Generate two paraphrased variations of the query.

      :param state: Workflow state containing 'user_query'.
      :type state: dict

      :returns: {'questions': {0: original, 1: rewrite1, 2: rewrite2}}
      :rtype: dict



   .. py:method:: run_classifications_parallel(state)

      Classify original query + rewrites in parallel.

      :param state: Workflow state containing 'questions'.
      :type state: dict

      :returns: {'query_classification': {0: [...], 1: [...], 2: [...]}}
      :rtype: dict



   .. py:method:: query_classification(state, level: int)

      Classify a query into one or more legal categories.

      :param state: Workflow state containing 'questions'.
      :type state: dict
      :param level: Which query variant to classify.
      :type level: int

      :returns: {'query_classification': {level: [query_text, index_keys]}}
      :rtype: dict



   .. py:method:: run_retrievals_parallel(state)

      Retrieve documents for each query variant in parallel.

      :param state: Workflow state with classifications.
      :type state: dict

      :returns: {'retrieved_docs': {0: [...], 1: [...], 2: [...]}}
      :rtype: dict



   .. py:method:: retrieve_docs(state, level: int)

      Retrieve docs for a single query variant.

      :param state: Workflow state with classifications.
      :type state: dict
      :param level: Which query variant to process.
      :type level: int

      :returns: List of [doc_text, metadata, score] or None if no indexes found.
      :rtype: list | None



   .. py:method:: get_context(state)

      Summarize retrieved documents into a coherent context.

      :param state: Workflow state containing 'retrieved_docs' and 'questions'.
      :type state: dict

      :returns: {'summarized_context': str} – the aggregated context string.
      :rtype: dict

      .. rubric:: Notes

      - Iterates through retrieval results for each query variant (0,1,2).

      - Summarizes each batch of retrieved documents via the LLM.

      - Concatenates summaries into a single combined context.



   .. py:method:: get_search_results(query: str)

      Perform Tavily web search and summarize results.

      :param query: User query in English.
      :type query: str

      :returns: {'search_results': str} – summarized context from Tavily results.
      :rtype: dict



   .. py:method:: initialize_workflow()

      Build the LangGraph workflow that wires together pipeline nodes.

      Nodes
      -----
      - query_rewriting → generate paraphrases
      - parallel_classification → classify all query variations
      - parallel_retrieval → retrieve docs for classified categories
      - get_context → summarize retrieved docs

      Edges
      -----
      query_rewriting → parallel_classification
      parallel_classification → parallel_retrieval
      parallel_retrieval → get_context

      :returns: Compiled LangGraph app with MemorySaver checkpointing.
      :rtype: StateGraph



   .. py:method:: run_full_pipeline(query: str)

      Execute the full RAG workflow for a user query.

      Steps
      -----
      1. starting_prompt → checks safety & domain.
      2. query_translation → ensures English query.
      3. Run web_search + rag_pipeline in parallel.
      4. Aggregate results: legal context + web results.

      :param query: Raw user query (any language).
      :type query: str

      :returns:

                If query is legal:
                    {
                    "query": translated_query, "summarized_context": str, "search_results": str, "language": str
                    }
                If query is non-legal or unsafe:
                    str – helpful or refusal message.
      :rtype: dict | str



