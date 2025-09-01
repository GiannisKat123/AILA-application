"""llm_pipeline
=================

A production-oriented, multilingual Retrieval-Augmented Generation (RAG) pipeline
specialized for legal question answering.

This module wires together:

- **Vector indexes** (via LlamaIndex) for multiple legal domains (Phishing, Law Cases,
  Greek Penal Code, GDPR), each with recall/precision variants where applicable.
- **Rerankers** using either a HuggingFace ``CrossEncoder`` model or a Cohere fine-tuned
  reranker model.
- **LangGraph** workflow that performs query rewriting (multi-variant), classification
  into legal categories, concurrent retrieval, and context summarization.
- **Multilingual handling**: detect input language, translate to English for retrieval
  if necessary, and preserve original language for responses.
- **Optional web search** to complement retrieved context.

The pipeline is encapsulated in :class:`LLM_Pipeline`, which exposes a single high-level
entrypoint :meth:`LLM_Pipeline.run_full_pipeline`.

This file includes Sphinx/Napoleon-compatible Google-style docstrings.

Prerequisites
-------------
- ``llama_index``
- ``langchain`` + ``langchain_openai`` + ``langchain_huggingface``
- ``langgraph``
- ``sentence_transformers`` (for CrossEncoder)
- ``cohere`` (for Cohere reranker)
- ``langdetect``
- ``openai`` (Responses API for web_search preview)

Environment/Settings
--------------------
The module expects a ``settings`` object (``backend.database.config.config.settings``)
that provides keys including (but not limited to):

- ``API_KEY``: OpenAI API key
- ``OPEN_AI_MODEL``: Chat model name for LangChain's ``ChatOpenAI``
- ``COHERE_API_KEY``: Cohere API key
- ``COHERE_MODEL_ID``: Base model id used for the Cohere finetuned reranker
- (Optionally) ``TAVILY_API_KEY`` if Tavily search is re-enabled

Notes
-----
- This module performs concurrent work using ``ThreadPoolExecutor`` in several places.
- The :class:`LLM_Pipeline` maintains a compiled LangGraph app (``self.app``) for the
  internal workflow, created in :meth:`LLM_Pipeline.initialize_workflow`.
"""

from backend.database.config.config import settings
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import load_index_from_storage
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from llama_index.core.retrievers import VectorIndexRetriever
from typing import Annotated, List, Dict, TypedDict
import cohere, ast
from cohere.finetuning.finetuning.types.get_finetuned_model_response import GetFinetunedModelResponse
from langdetect import detect
from langchain.prompts import PromptTemplate 
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4
import operator 
from openai.cli._errors import OpenAIError
from langchain_core.documents.base import Document as langchainDocument
from langchain_tavily import TavilySearch
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from openai import OpenAI


def load_vector_index(top_k: int, persist_dir: str, embedding):
    """Load a persisted LlamaIndex vector index and return a retriever.

    The index is restored from ``persist_dir`` with the provided embedding model
    and returned as a :class:`~llama_index.core.retrievers.VectorIndexRetriever`
    configured for hybrid search.

    Args:
        top_k: Number of top similar results to retrieve on search.
        persist_dir: Filesystem directory where the index is persisted.
        embedding: An embedding model instance compatible with LlamaIndex
            (e.g., ``HuggingFaceEmbeddings`` or ``OpenAIEmbedding``).

    Returns:
        VectorIndexRetriever: A retriever instance with ``similarity_top_k`` set
        to ``top_k`` and ``search_type='hybrid'``.
    """
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context, embed_model=embedding)
    return index.as_retriever(similarity_top_k=top_k, search_type='hybrid')


def load_reranker_model():
    """Initialize and fetch the Cohere fine-tuned reranker model handle.

    Uses the ``COHERE_API_KEY`` and ``COHERE_MODEL_ID`` from ``settings`` to
    instantiate a Cohere V2 client and retrieve the finetuned model metadata.

    Returns:
        tuple[cohere.ClientV2, GetFinetunedModelResponse]:
            A tuple of the initialized Cohere client and the fine-tuned model
            response object (metadata/handle). The returned model is suitable
            for use with ``client.rerank`` via ``model=f"{id}-ft"``.
    """
    co = cohere.ClientV2(settings.COHERE_API_KEY)
    ft = co.finetuning.get_finetuned_model(settings.COHERE_MODEL_ID)
    return co, ft


def initialize_indexes(top_k: int):
    """Load all domain-specific vector retrievers used by the pipeline.

    The following domains are initialized (each with a specific cached
    embedding model and persisted index directory):

    - Phishing scenarios
    - Law Cases (recall + precision)
    - Greek Penal Code (recall + precision)
    - GDPR (recall + precision)

    Args:
        top_k: Default ``similarity_top_k`` for each retriever.

    Returns:
        dict[str, VectorIndexRetriever]: A mapping from domain key to retriever.

    Notes:
        Embedding models are expected to be available locally in the specified
        ``./backend/cached_embedding_models`` directories.
    """

    # 🔐 Phishing
    phishing_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/phishing_index_documents_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__multilingual-e5-large-legal-matryoshka'),
    )

    # ⚖️ Law Cases – Recall
    law_cases_index_recall_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/law_cases_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )

    # ⚖️ Law Cases – Precision
    law_cases_index_precision_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/law_cases_recall_index_documents_precision_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__bge-m3-legal-matryoshka'),
    )

    # 🇬🇷 Greek Penal Code – Recall
    gpc_index_recall_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/gpc_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__legal-bert-base-uncased-legal-matryoshka'),
    )

    # 🇬🇷 Greek Penal Code – Precision
    gpc_index_precision_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/gpc_recall_index_documents_precision_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )

    # 🛡️ GDPR – Recall
    gdpr_index_recall_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/gdpr_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )

    # 🛡️ GDPR – Precision
    gdpr_index_precision_retriever = load_vector_index(
        top_k,
        "./backend/vector_indexes/gdpr_precision_index_documents_precision_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__multilingual-e5-large-legal-matryoshka'),
    )

    return {
        "phishing_retriever": phishing_retriever,
        "law_cases_index_recall_retriever": law_cases_index_recall_retriever,
        "law_cases_index_precision_retriever": law_cases_index_precision_retriever,
        "gpc_index_recall_retriever": gpc_index_recall_retriever,
        "gpc_index_precision_retriever": gpc_index_precision_retriever,
        "gdpr_index_recall_retriever": gdpr_index_recall_retriever,
        "gdpr_index_precision_retriever": gdpr_index_precision_retriever,
    }


class AgentState(TypedDict):
    """LangGraph state for the legal assistant workflow.

    Keys
    ----
    user_query:
        The canonical user query (possibly rewritten) used for retrieval.
    summarized_context:
        The aggregated, summarized context assembled from retrieved documents.
    search_results:
        A summarized web-search snippet (if available).
    questions:
        Variants of the user query produced by query rewriting
        (3 entries: original + 2 variants).
    query_classification:
        Mapping from variant index to ``[variant_text, index_keys]`` where
        ``index_keys`` is a list of retriever keys to use for retrieval.
    retrieved_docs:
        Mapping from variant index to retrieval results (already reranked).
    context:
        Arbitrary context dictionary (reserved for future extensions).
    """

    user_query: str
    summarized_context: str
    search_results: str
    questions: List[str]
    query_classification: Annotated[Dict[str, List[str]], operator.or_]
    retrieved_docs: Annotated[Dict[str, List], operator.or_]
    context: Annotated[Dict[str, str], operator.or_]


class LLM_Pipeline:
    """End-to-end legal RAG pipeline with classification, retrieval, and summarization.

    This class encapsulates the entire pipeline and exposes:

    - Initialization with pre-loaded retrievers and reranker model
    - A compiled LangGraph workflow (``self.app``)
    - A high-level :meth:`run_full_pipeline` orchestrating classification,
      translation, web search, retrieval, and summarization

    Args:
        index_mapping: Mapping from string keys to :class:`VectorIndexRetriever`
            instances. Keys must match those emitted by ``query_classification``.
        reranker_model: Either a HuggingFace ``CrossEncoder`` for local reranking or
            a Cohere :class:`GetFinetunedModelResponse` that designates a server-side
            fine-tuned reranker.
        cohere_client: Optional Cohere V2 client; **required** when ``reranker_model``
            is a Cohere fine-tuned model.
    """

    def __init__(
        self,
        index_mapping: dict[str, VectorIndexRetriever],
        reranker_model: CrossEncoder | GetFinetunedModelResponse,
        cohere_client: cohere.ClientV2 | None = None,
    ):
        self.cohere_client = cohere_client
        self.index_mapping = index_mapping
        self.reranker_model = reranker_model
        self.client = OpenAI(api_key=settings.API_KEY)
        self.model = ChatOpenAI(model=settings.OPEN_AI_MODEL, api_key=settings.API_KEY, temperature=0.7)
        self.dict_lang = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "ru": "Russian",
            "ja": "Japanese",
            "zh-cn": "Chinese (Simplified)",
            "zh-tw": "Chinese (Traditional)",
            "ko": "Korean",
            "ar": "Arabic",
            "hi": "Hindi",
            "bn": "Bengali",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "pl": "Polish",
            "uk": "Ukrainian",
            "el": "Greek",
            "ro": "Romanian",
            "sv": "Swedish",
            "fi": "Finnish",
            "no": "Norwegian",
            "da": "Danish",
            "hu": "Hungarian",
            "cs": "Czech",
            "sk": "Slovak",
            "ca": "Catalan",
            "id": "Indonesian",
            "ms": "Malay",
            "th": "Thai",
            "fa": "Persian",
            "he": "Hebrew",
        }
        self.app = self.initialize_workflow()

    def retrieving_docs(
        self,
        query: str,
        index_mapping: dict[str, VectorIndexRetriever],
        indexes: List[VectorIndexRetriever],
        reranker_model: CrossEncoder | GetFinetunedModelResponse,
        cohere_client: cohere.client_v2.ClientV2 | None,
    ):
        """Retrieve and rerank documents for a query from multiple indexes.

        This function retrieves raw nodes from each requested retriever and then
        reranks them globally using either a local HuggingFace ``CrossEncoder``
        or the Cohere fine-tuned reranker. The final output is a top-N list of
        documents with scores and metadata.

        Args:
            query: The user query to search for.
            index_mapping: Mapping from retriever key to retriever instance.
            indexes: A list of retriever **keys** to use for retrieval.
            reranker_model: The reranker to apply (local or Cohere FT handle).
            cohere_client: Cohere client required for Cohere reranking.

        Returns:
            list[list]: A list of ``[text, metadata, score]`` triples representing
            the reranked top results across all provided indexes.
        """
        retrieved_nodes = []
        for index in indexes:
            index = index_mapping[index]
            nodes = index.retrieve(query)
            retrieved_nodes.append([langchainDocument(page_content=node.text, metadata=node.metadata) for node in nodes])

        if isinstance(reranker_model, CrossEncoder):
            documents = []
            for index_nodes in retrieved_nodes:
                documents += [node for node in index_nodes]

            pairs = [(query, doc.page_content) for doc in documents]

            # Predict relevance scores and sort descending
            scores = reranker_model.predict(pairs)
            scored_docs = list(zip(scores, documents))
            scored_docs.sort(reverse=True, key=lambda x: x[0])

            top_n = 10
            reranked_docs = scored_docs[:top_n]
            return [[node.page_content, node.metadata, float(score)] for score, node in reranked_docs]

        if isinstance(reranker_model, GetFinetunedModelResponse) and cohere_client:
            documents_texts = []
            documents = []
            for index_nodes in retrieved_nodes:
                for node in index_nodes:
                    documents_texts.append(node.page_content)
                    documents.append([node.page_content, node.metadata])

            response = cohere_client.rerank(
                query=query,
                documents=documents_texts,
                model=reranker_model.finetuned_model.id + "-ft",
            )

            results = response.results
            doc_indexing = [item.index for item in results]
            relevance_scores = [item.relevance_score for item in results]

            return [[documents[i][0], documents[i][1], relevance_scores[i]] for i in doc_indexing]

    def starting_prompt(self, conversation_history: List[str], query: str):
        """Rewrite follow-up queries and classify scope (legal vs non-legal).

        If there is prior ``conversation_history``, the latest user turn is used
        to rewrite ``query`` into a standalone question that preserves entities.
        Regardless of rewriting, the method then performs a **strict** legal-scope
        classification (returns ``"True"`` or ``"False"`` as strings).

        Args:
            conversation_history: A list of past messages (assumed dicts with
                ``message`` keys) to provide conversational context.
            query: The latest user input.

        Returns:
            tuple[str, str]: A pair ``(is_legal_scope, possibly_rewritten_query)``
            where ``is_legal_scope`` is either ``"True"`` or ``"False"``.
        """
        print(conversation_history)

        if conversation_history:
            prompt = """
            You are a query rewriter for a legal assistant.
            Using the conversation and the latest user message, produce ONE standalone question that
            preserves the same intent and keeps entities/sections exact.
            - Keep language the same as the user's latest message.
            - Output ONLY the rewritten question, no quotes, no extra text.

            Conversation (oldest→newest):
            {history}

            Latest user message:
            {query}

            Rewritten standalone question:
            """

            history = [mes['message'] for mes in conversation_history][-1]

            print(prompt.format(query=query, history=history))

            response = self.model.invoke(prompt.format(query=query, history=history))
            response_content = str(response.content).strip()
            print(response_content)
            query = response_content

        print(query)

        prompt = """
        You are a STRICT CLASSIFIER for a legal assistant. Do NOT answer questions.

        SCOPE = LEGAL if the query is about laws, regulations, rights/obligations, court cases, procedures, penalties, contracts, privacy/data protection (e.g., GDPR), cybercrime (e.g., phishing, SIM swap, bank fraud), phishing scenarios (e.g. Smishing, Quishing, etc.), compliance, liability, or legal interpretations—whether general or specific, in any language.

        If the SCOPE is legal return True else False

        RULES
        - If the topic is within SCOPE → True
            For example:
                What are some forms of quishing attacks -> True
        - If outside SCOPE (math, travel, coding help, general trivia, etc.) → False
        - No explanations, no extra fields, no markdown.

        USER
        {query}

        """

        response = self.model.invoke(prompt.format(query=query))
        response_content = str(response.content).strip()
        print(response_content)
        return response_content, query

    def query_translation(self, query: str):
        """Detect language and translate non-English queries to English.

        The detected language code (e.g., ``'el'``) is mapped to a human-readable
        name via ``self.dict_lang``. If the input is not English, the query is
        translated to English using the chat model; otherwise it is returned as-is.

        Args:
            query: The original (possibly non-English) user query.

        Returns:
            tuple[str, str]: ``(language_name, english_query)`` where
            ``language_name`` is a human-readable language label and
            ``english_query`` is the translated or original query.
        """
        lang = detect(query)
        if lang != 'en':
            prompt = """
            You are a highly competent legal assistant. Your task is to accurately translate the following legal query into English while preserving its original meaning, legal terminology, and nuance.

            Text to translate:
            {query}

            Provide only the translated version. Do not explain, rephrase, or annotate. 
            """

            response = self.model.invoke(prompt.format(query=query))
            response_content = str(response.content).strip()
            query = response_content

        language = self.dict_lang[lang]
        return language, query

    def web_search(self, query: str):
        """Perform a lightweight web search via OpenAI's web_search_preview tool.

        This method uses the OpenAI Responses API with the experimental
        ``web_search_preview`` tool to obtain a short, model-generated summary of
        public web results related to ``query``.

        Args:
            query: The search query string.

        Returns:
            dict: ``{"search_results": str}`` containing summarized results text.

        Notes:
            The (commented) Tavily implementation can be re-enabled if desired,
            which returns richer structured search data at the cost of an extra
            dependency and additional tokens.
        """
        # --- Alternative Tavily implementation (kept for reference) ---
        # search_tool = TavilySearch(
        #     max_results=5,
        #     include_answer=True,
        #     include_raw_content=True,
        #     include_images=False,
        #     tavily_api_key=settings.TAVILY_API_KEY,
        # )
        # search_results = search_tool.invoke({"query": query})
        # summarized_prompt = """
        #     You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.
        #     I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
        #     Context:{summarized_context}
        #     User Query:{query}
        # """
        # response = self.model.invoke(summarized_prompt.format(
        #     query=query,
        #     summarized_context='\n'.join(f'{result["title"]} (score:{result["score"]}) url:{result["url"]} content:{result["content"]}' for result in search_results['results'])
        # ))
        # summarized_context = str(response.content).strip()
        # return {'search_results': summarized_context}

        summarized_context = self.client.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
        return {'search_results': summarized_context.output_text}

    def rag_pipeline(self, query: str, app):
        """Execute the internal LangGraph workflow to build summarized context.

        Args:
            query: The canonical (English) user query to process.
            app: A compiled LangGraph application returned by
                :meth:`initialize_workflow`.

        Returns:
            dict: A mapping with ``{"query": query, "summarized_context": str}``.
        """
        config = {"configurable": {"thread_id": f"{uuid4()}"}}
        result = app.invoke(
            {
                "user_query": query,
                "questions": [],
                "query_classification": {},
                "retrieved_docs": {},
                "context": {},
            },
            config,
        )
        return {"query": query, 'summarized_context': result['summarized_context']}

    def query_rewriting(self, state):
        """Create two semantically similar rewrites of the user's query.

        The function writes three entries into ``state['questions']``:
        index ``0`` is the original query, and ``1``/``2`` are diverse rewrites.

        Args:
            state (AgentState): The LangGraph state (dict-like) that contains at
                least ``'user_query'``.

        Returns:
            dict: ``{"questions": {0: original, 1: rewrite1, 2: rewrite2}}`` suitable
            for LangGraph state updates.

        Raises:
            RuntimeError: If a transient OpenAI error reoccurs or parsing fails
                after multiple attempts.
        """
        prompt = """
        Rewrite the following user query into 2 semantically similar but linguistically diverse variations.

        Original query:
        "{query}"

        Instructions:
        - Maintain the original intent.
        - Vary the vocabulary and phrasing.
        - Keep the rewrites concise and clear.
        - Avoid repeating phrases from the original query verbatim.

        Return your response as a list formatted like:
        Output: ["First variation", "Second variation"]
        """

        retries = 3
        for _ in range(retries):
            try:
                response = self.model.invoke(prompt.format(query=state['user_query']))
                response_content = str(response.content).strip()
                res = response_content.split("Output:")
                res = ast.literal_eval(res[1])
                questions = {0: state['user_query'], 1: res[0], 2: res[1]}
                state['questions'] = questions
                return {'questions': questions}

            except OpenAIError:
                raise RuntimeError("Exceeded current quota, please contact the administrator.")
            except Exception:
                continue

        raise RuntimeError("❌ Failed to rewrite query after multiple attempts.")

    def run_classifications_parallel(self, state):
        """Classify the original + rewrites concurrently into legal domains.

        For each of the three query variants (indices 0–2), run
        :meth:`query_classification` and combine the results into a single
        mapping under ``state['query_classification']``.

        Args:
            state (AgentState): The pipeline state with ``'questions'`` set.

        Returns:
            dict: ``{"query_classification": {i: [text, index_keys], ...}}``
            suitable for LangGraph state updates.
        """
        levels = [0, 1, 2]
        results = {}

        def classify(level):
            try:
                result = self.query_classification(state, level)
                return level, result
            except Exception:
                return level, {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(classify, level): level for level in levels}
            for future in as_completed(futures):
                level, result = future.result()
                results[level] = result

        combined = {}
        for i in range(3):
            combined[i] = results[i]['query_classification'][i]
        state['query_classification'] = combined
        return {'query_classification': state['query_classification']}

    def query_classification(self, state, level: int):
        """Classify one query variant into legal categories and pick indexes.

        The classifier outputs a list of categories among:
            ``["Phishing Scenarios", "Specific Legal Cases", "GDPR", "Greek Penal Code"]``.

        Categories map to retriever keys used later during retrieval:

        - ``GDPR`` → ``["gdpr_index_recall_retriever", "gdpr_index_precision_retriever"]``
        - ``Greek Penal Code`` → ``["gpc_index_recall_retriever", "gpc_index_precision_retriever"]``
        - ``Specific Legal Cases`` → ``["law_cases_index_recall_retriever", "law_cases_index_precision_retriever"]``
        - ``Phishing Scenarios`` → ``["phishing_retriever"]``

        Args:
            state (AgentState): The current pipeline state containing
                ``state['questions'][level]``.
            level: The query variant index (0, 1, or 2).

        Returns:
            dict: ``{"query_classification": {level: [text, index_keys]}}`` suitable
            for LangGraph state updates. If parsing fails or no categories are
            returned, ``index_keys`` may be ``None``.
        """
        prompt ="""  
            You are a legal assistant. Your task is to classify a user's query into one or more of the following legal categories:

            1) Phishing Scenarios  
            2) Specific Legal Cases  
            3) GDPR  
            4) Greek Penal Code

            Classify the query based on its subject and context. Always return your output as a list of relevant categories.

            Examples:

            User Query: What is Phishing?  
            Output: ["Phishing Scenarios"]

            User Query: What is GDPR?  
            Output: ["GDPR"]

            User Query: How can phishing be punished in Greek Legislation?  
            Output: ["Greek Penal Code"]

            User Query: What is Phishing and give me an example of such case  
            Output: ["Phishing Scenarios", "Specific Legal Cases"]

            Now classify this query:  
            "{query}"

        """

        response = self.model.invoke(prompt.format(query=state['questions'][level]))
        response_content = str(response.content).strip()

        res = response_content.split("Output:")
        if len(res) > 1:
            res = res[1]
        else:
            res = res[0]

        if isinstance(res, list) and isinstance(res[0], str):
            res = res[0]

        try:
            categories = ast.literal_eval(res)

            if len(categories) > 0:
                indexes = []
                for category in categories:
                    if category == 'GDPR':
                        indexes += ["gdpr_index_recall_retriever", "gdpr_index_precision_retriever"]
                    if category == 'Greek Penal Code':
                        indexes += ["gpc_index_recall_retriever", "gpc_index_precision_retriever"]
                    if category == 'Specific Legal Cases':
                        indexes += ["law_cases_index_recall_retriever", "law_cases_index_precision_retriever"]
                    if category == 'Phishing Scenarios':
                        indexes += ["phishing_retriever"]
                state['query_classification'] = {level: [state['questions'][level], indexes]}
            else:
                state['query_classification'] = {level: [state['questions'][level], None]}

        except Exception:
            state['query_classification'] = {level: [state['questions'][level], None]}

        return {'query_classification': state['query_classification']}

    def run_retrievals_parallel(self, state):
        """Retrieve documents for all variants concurrently.

        For each classified variant (0–2), call :meth:`retrieve_docs` in a thread
        and assemble the results into ``state['retrieved_docs']``.

        Args:
            state (AgentState): The pipeline state that must include
                ``'query_classification'`` and ``'questions'`` keys.

        Returns:
            dict: ``{"retrieved_docs": {level: results, ...}}`` suitable for state
            updates in LangGraph.
        """
        levels = [0, 1, 2]
        results = {}

        def retrieve(level):
            return level, self.retrieve_docs(state, level)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(retrieve, level): level for level in levels}
            for future in as_completed(futures):
                level, result = future.result()
                results[level] = result

        state['retrieved_docs'] = results
        return {'retrieved_docs': state['retrieved_docs']}

    def retrieve_docs(self, state, level):
        """Retrieve/rerank documents for a specific query variant.

        Args:
            state (AgentState): The workflow state with ``questions`` and
                ``query_classification`` populated.
            level: The query variant index (0, 1, or 2).

        Returns:
            dict: ``{level: [[text, metadata, score], ...]}`` placed under
            ``state['retrieved_docs'][level]``. If no indexes are mapped, the
            value is ``None``.
        """
        retrieved_documents = self.retrieving_docs(
            state['questions'][0],
            self.index_mapping,
            state['query_classification'][level][1],
            self.reranker_model,
            self.cohere_client,
        ) if state['query_classification'][level][1] else None
        state['retrieved_docs'][level] = retrieved_documents
        return {level: state['retrieved_docs'][level]}

    def get_context(self, state):
        """Summarize retrieved results into a compact, answer-ready context.

        For each level (0–2), join top reranked hits into a single text block
        enriched with scores and metadata, and ask the chat model to summarize
        **only** the content relevant to that variant. The final output is the
        concatenation of all non-empty summaries.

        Args:
            state (AgentState): The pipeline state containing ``retrieved_docs``
                and ``questions``.

        Returns:
            dict: ``{"summarized_context": str}`` — a merged summary string.
        """
        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        def summarize_level(level: int):
            if not state['retrieved_docs'][level]:
                return level, ""
            print(state['retrieved_docs'][level])
            retrieved_documents = state['retrieved_docs'][level][level]
            if retrieved_documents == None:
                return level, ""
            if len(retrieved_documents) == 0:
                return level, ""

            joined_context = '\n'.join(
                f"{i}) {retrieved_documents[i][0]} (score:{retrieved_documents[i][2]}) metadata:{retrieved_documents[i][1]}"
                for i in range(len(retrieved_documents))
            )

            response = self.model.invoke(
                summarized_prompt.format(
                    query=state['questions'][level],
                    summarized_context=joined_context,
                )
            )

            return level, str(response.content).strip()

        summarized_by_level = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(summarize_level, level): level for level in range(3)}
            for future in as_completed(futures):
                level, summary = future.result()
                summarized_by_level[level] = summary

        full_summary = "\n\n".join(
            summarized_by_level[i] for i in range(3) if i in summarized_by_level
        )
        return {'summarized_context': full_summary}

    def initialize_workflow(self):
        """Build and compile the LangGraph workflow used by the pipeline.

        Nodes:
            - ``query_rewriting`` → produce two rewrite variants
            - ``parallel_classification`` → classify original + rewrites
            - ``parallel_retrieval`` → concurrently retrieve documents per variant
            - ``get_context`` → summarize per-variant context and merge

        Returns:
            Any: A compiled LangGraph app instance (opaque), stored on
            ``self.app`` and used internally by :meth:`rag_pipeline`.
        """
        workflow = StateGraph(AgentState)

        # Query re-writing
        workflow.add_node('query_rewriting', self.query_rewriting)
        # Query Categorization of query and variants
        workflow.add_node('parallel_classification', self.run_classifications_parallel)
        # Document Retrieval
        workflow.add_node('parallel_retrieval', self.run_retrievals_parallel)
        # Document Aggregation and Response
        workflow.add_node('get_context', self.get_context)

        # Edges
        workflow.add_edge('query_rewriting', 'parallel_classification')
        workflow.add_edge('parallel_classification', 'parallel_retrieval')
        workflow.add_edge('parallel_retrieval', 'get_context')

        workflow.set_entry_point('query_rewriting')
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)
        return app

    def run_full_pipeline(self, query: str, conversation_history: List[str], app):
        """Run the full legal pipeline: scope check, translation, web + RAG.

        The method first checks if the query is **legal** in scope using
        :meth:`starting_prompt`. If legal, it translates the query to English
        (if needed), launches web search and the RAG workflow concurrently, and
        returns a combined payload. If **not** legal, it produces a brief, safe
        non-legal response (while reminding the user that this is a legal
        assistant) in the user's language.

        Args:
            query: Raw user question.
            conversation_history: Prior conversation (for better rewriting). A
                list where each element is expected to be a dict with a
                ``'message'`` key.
            app: Compiled LangGraph app returned by
                :meth:`initialize_workflow`.

        Returns:
            dict | str: If legal, a dict with keys ``query``, ``summarized_context``,
            ``search_results``, and ``language``. If not legal, a string response
            that addresses the query briefly and safely.
        """
        res, new_query = self.starting_prompt(conversation_history, query)
        print(res, new_query)
        if res.lower() == 'true':
            language, translated_query = self.query_translation(new_query)

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_search = executor.submit(self.web_search, translated_query)
                future_rag = executor.submit(self.rag_pipeline, translated_query, app)

            return {
                "query": translated_query,
                'summarized_context': future_rag.result()['summarized_context'],
                'search_results': future_search.result()['search_results'],
                "language": language,
            }

        else:
            lang = detect(new_query)
            prompt = """
            You are a highly competent legal assistant. You answer questions that are non-legal and possibly out of knowledge. 
            
            You goal is to provide a short answer to the user question but always make sure that you make your role known to the user.

            For example:

                If non-legal:  "Helpful, short answer **plus** a clear reminder that you are a legal assistant."
                If the query is inappropriate, illegal, or unsafe: "I'm a legal assistant. I cannot answer unsafe or inappropriate questions."

            SAFETY RULES:
                - NEVER provide advice about:
                    - Medical conditions or treatments
                    - Mental health or suicide
                    - Financial advice or investments
                    - Hacking, fraud, or illegal activities
                    - Politics, religion, or violent topics
                    - If the query is unsafe or inappropriate, respond: "I'm a legal assistant. I cannot answer unsafe or inappropriate questions."
                - If the question is just general (like math, geography, etc.), answer the question briefly and remind the user that you are a legal assistant.
                    For example:
                        User Query: What is the capital of France?
                        Response: "The capital of France is Paris. I am a legal assistant and can only provide legal information."

            ROLE GUIDELINES:
                - Stay in character: you're a **legal assistant**, not a doctor, therapist, investor, or general assistant.
                - Be professional, respectful, and neutral.
                - Respond in {lang}

            User Query: {query}
            """

            response = self.model.invoke(prompt.format(query=new_query, lang=self.dict_lang[lang]))
            response_content = str(response.content).strip()
            return response_content
