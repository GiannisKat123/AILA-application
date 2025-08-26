"""
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
   -> Preloads all vector indexes (Phishing, Law Cases Recall/Precision,
      Greek Penal Code Recall/Precision, GDPR Recall/Precision).

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
"""

from backend.database.config.config import settings
from llama_index.core import StorageContext, load_index_from_storage
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from llama_index.core.retrievers import VectorIndexRetriever
from typing import Annotated, List, Dict, TypedDict
import cohere, ast, time, operator
from cohere.finetuning.finetuning.types.get_finetuned_model_response import GetFinetunedModelResponse
from langdetect import detect
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4
from openai.cli._errors import OpenAIError
from langchain_core.documents.base import Document as langchainDocument
from langchain_tavily import TavilySearch
from concurrent.futures import ThreadPoolExecutor, as_completed


# -------------------------
# Index / Reranker Loading
# -------------------------
def load_vector_index(top_k: int, persist_dir: str, embedding):
    """
    Load a LlamaIndex vector index with a specified embedding model.

    Parameters
    ----------
    top_k : int
        Max number of docs to retrieve.
    persist_dir : str
        Directory containing the persisted index.
    embedding : HuggingFaceEmbeddings
        Embedding model to use for retrieval.

    Returns
    -------
    VectorIndexRetriever
        A retriever configured for hybrid search with similarity top_k.
    """
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context, embed_model=embedding)
    return index.as_retriever(similarity_top_k=top_k, search_type="hybrid")


def load_reranker_model():
    """
    Load a Cohere client and finetuned reranker model.

    Returns
    -------
    tuple
        (Cohere client, finetuned model reference)
    """
    co = cohere.ClientV2(settings.COHERE_API_KEY)
    ft = co.finetuning.get_finetuned_model(settings.COHERE_MODEL_ID)
    return co, ft


def initialize_indexes(top_k: int):
    """
    Initialize and return all domain-specific retrievers.

    Domains:
    - Phishing
    - Law Cases (Recall & Precision)
    - Greek Penal Code (Recall & Precision)
    - GDPR (Recall & Precision)

    Returns
    -------
    dict[str, VectorIndexRetriever]
    """
    return {
        # 🛡 Phishing
        "phishing_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/phishing_index_documents_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__multilingual-e5-large-legal-matryoshka"),
        ),
        # ⚖️ Law Cases
        "law_cases_index_recall_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/law_cases_recall_index_documents_recall_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2"),
        ),
        "law_cases_index_precision_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/law_cases_recall_index_documents_precision_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__bge-m3-legal-matryoshka"),
        ),
        # 🇬🇷 Greek Penal Code
        "gpc_index_recall_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/gpc_recall_index_documents_recall_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__legal-bert-base-uncased-legal-matryoshka"),
        ),
        "gpc_index_precision_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/gpc_recall_index_documents_precision_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2"),
        ),
        # 🛡 GDPR
        "gdpr_index_recall_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/gdpr_recall_index_documents_recall_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2"),
        ),
        "gdpr_index_precision_retriever": load_vector_index(
            top_k,
            "./backend/vector_indexes/gdpr_precision_index_documents_precision_trained_embedding",
            HuggingFaceEmbeddings(model_name="./backend/cached_embedding_models/IoannisKat1__multilingual-e5-large-legal-matryoshka"),
        ),
    }


# -------------------------
# LangGraph State
# -------------------------
class AgentState(TypedDict):
    """Shared state for the pipeline's LangGraph workflow."""
    user_query: str
    summarized_context: str
    search_results: str
    questions: List[str]
    query_classification: Annotated[Dict[str, List[str]], operator.or_]
    retrieved_docs: Annotated[Dict[str, List], operator.or_]
    context: Annotated[Dict[str, str], operator.or_]


# -------------------------
# LLM Pipeline Orchestrator
# -------------------------
class LLM_Pipeline:
    """
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

    Attributes
    ----------
    index_mapping : dict[str, VectorIndexRetriever]
        Preloaded retrievers.
    reranker_model : CrossEncoder | GetFinetunedModelResponse
        Model used to rerank retrieved documents.
    cohere_client : cohere.ClientV2 | None
        Optional client for Cohere reranking.
    model : ChatOpenAI
        LLM used for classification, rewriting, summarization.
    """

    def __init__(self, index_mapping, reranker_model, cohere_client=None):
        self.cohere_client = cohere_client
        self.index_mapping = index_mapping
        self.reranker_model = reranker_model
        self.model = ChatOpenAI(
            model=settings.OPEN_AI_MODEL,
            api_key=settings.API_KEY,
            temperature=0.7,
        )
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
            "he": "Hebrew"
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
        """
        Retrieve and rerank documents for a given query.

        Parameters
        ----------
        query : str
            The user query (in English, after translation).
        index_mapping : dict[str, VectorIndexRetriever]
            Mapping of index keys to retrievers.
        indexes : list[str]
            Keys from index_mapping specifying which retrievers to query.
        reranker_model : CrossEncoder | GetFinetunedModelResponse
            Model used to rerank results. Supports SentenceTransformer CrossEncoder
            or a Cohere finetuned model reference.
        cohere_client : cohere.ClientV2 | None
            Cohere client, required if reranker_model is Cohere.

        Returns
        -------
        list[list]
            List of [doc_text, metadata, score] for top reranked documents.
        """
        retrieved_nodes = []
        for index in indexes:
            index = index_mapping[index]
            nodes = index.retrieve(query)
            retrieved_nodes.append([langchainDocument(page_content=node.text,metadata=node.metadata) for node in nodes])

        if isinstance(reranker_model,CrossEncoder):
            documents = []
            for index_nodes in retrieved_nodes:
                documents += [node for node in index_nodes]

            pairs = [(query, doc.page_content) for doc in documents]

            # Step 2: Get scores from the model
            scores = reranker_model.predict(pairs)  # This returns a list of floats

            # Step 3: Zip scores with documents
            scored_docs = list(zip(scores, documents))

            # Step 4: Sort by score descending (like reranker does internally)
            scored_docs.sort(reverse=True, key=lambda x: x[0])

            # Step 5: Select top_n
            top_n = 10
            reranked_docs = scored_docs[:top_n]

            return [[node.page_content,node.metadata,float(score)] for score, node in reranked_docs]

        if isinstance(reranker_model,GetFinetunedModelResponse) and cohere_client:
            documents_texts = []
            documents = []
            for index_nodes in retrieved_nodes:
                for node in index_nodes:
                    documents_texts.append(node.page_content)
                    documents.append([node.page_content,node.metadata])
            
            response = cohere_client.rerank(
                query=query,
                documents=documents_texts,
                model=reranker_model.finetuned_model.id + "-ft",
            )

            results = response.results
            doc_indexing = [item.index for item in results]
            relevance_scores = [item.relevance_score for item in results]

            return [[documents[i][0],documents[i][1],relevance_scores[i]] for i in doc_indexing]

    def starting_prompt(self, query: str):
        """
        Classify a query as legal, non-legal, or unsafe.

        Behavior
        --------
        - If legal: returns [True, None]
        - If non-legal: returns [False, "<short helpful answer + reminder>"]
        - If unsafe (medical, financial, illegal, etc.): returns
          [False, "I'm a legal assistant. I cannot answer unsafe..."]

        Parameters
        ----------
        query : str
            The raw user query.

        Returns
        -------
        list
            [bool, str | None] indicating if legal and optional message.
        """
        lang = detect(query)
        prompt = """
            You are a highly competent legal assistant.

            Your job is to:
            1. Determine whether the following user query is a **legal** question.
            2. If non-legal: [False, "Helpful, short answer **plus** a clear reminder that you are a legal assistant."]
            3. If the query is inappropriate, illegal, or unsafe: [False, "I'm a legal assistant. I cannot answer unsafe or inappropriate questions."]

            SAFETY RULES:
                - NEVER provide advice about:
                    - Medical conditions or treatments
                    - Mental health or suicide
                    - Financial advice or investments
                    - Hacking, fraud, or illegal activities
                    - Politics, religion, or violent topics
                    - If the query is unsafe or inappropriate, respond:
                    [False, "I'm a legal assistant. I cannot answer unsafe or inappropriate questions."]
                - If the question is just general (like math, geography, etc.), answer the question briefly and remind the user that you are a legal assistant.
                    For example:
                        User Query: What is the capital of France?
                        Response: [False, "The capital of France is Paris. However, I am a legal assistant and can only provide legal information."]

            ROLE GUIDELINES:
                - Stay in character: you're a **legal assistant**, not a doctor, therapist, investor, or general assistant.
                - Be professional, respectful, and neutral.
                - Respond in {lang}

            FORMAT:
                - You must respond ONLY in this exact format:
                [True, None] or [False, "Your message here"]

            ---

            User Query: {query}

        """    

        response = self.model.invoke(prompt.format(query=query,lang=self.dict_lang[lang]))
        response_content = str(response.content).strip()
        res = ast.literal_eval(response_content)
        return res


    def query_translation(self, query: str):
        """
        Translate query into English if necessary.

        Parameters
        ----------
        query : str
            User query in any supported language.

        Returns
        -------
        tuple
            (language_name, translated_query)
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
        return language,query
    
    def web_search(self, query: str):
        """
        Perform a web search via TavilySearch and summarize results.

        Parameters
        ----------
        query : str
            User query (in English).

        Returns
        -------
        dict
            {'search_results': str} summarizing retrieved context.
        """
        search_tool = TavilySearch(
            max_results=5,
            include_answer=True,
            include_raw_content=True,
            include_images=False,
            tavily_api_key=settings.TAVILY_API_KEY,
        )

        search_results = search_tool.invoke({"query": query})

        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        response = self.model.invoke(summarized_prompt.format(
            query=query,
            summarized_context='\n'.join(f'{result["title"]} (score:{result["score"]}) url:{result["url"]} content:{result["content"]}' for result in search_results)
        ))

        summarized_context = str(response.content).strip()
        return {'search_results': summarized_context}
    
    def rag_pipeline(self, query: str):
        """
        Run the LangGraph workflow (query rewriting -> classification -> retrieval -> context).

        Parameters
        ----------
        query : str
            User query in English.

        Returns
        -------
        dict
            {
              'query': query,
              'summarized_context': str
            }
        """
        config = {"configurable": {"thread_id": f"{uuid4()}"}}
        result = self.app.invoke({
            "user_query":query,
            "questions": [],  # <-- ADD THIS
            "query_classification": {},  # <-- FIXED
            "retrieved_docs": {},  # <-- ADD THIS
            "context": {},  # <-- ALREADY GOOD
        }, config)

        return {"query":query,
            'summarized_context':result['summarized_context'],
            }
    
    def query_rewriting(self, state):
        """
        Generate two paraphrased variations of the query.

        Parameters
        ----------
        state : dict
            Workflow state containing 'user_query'.

        Returns
        -------
        dict
            {'questions': {0: original, 1: rewrite1, 2: rewrite2}}
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
                response = self.model.invoke(prompt.format(query = state['user_query']))

                response_content = str(response.content).strip()
                res = response_content.split("Output:")
                res = ast.literal_eval(res[1])
                questions = {0:state['user_query'],1:res[0],2:res[1]}

                state['questions'] = questions
                return {'questions':questions}
            
            except OpenAIError:
                raise RuntimeError("Exceeded current quota, please contact the administrator.")  # ✅ Fixed
            
            except Exception as e:
                continue  
        
        raise RuntimeError("❌ Failed to rewrite query after multiple attempts.")

    def run_classifications_parallel(self, state):
        """
        Classify original query + rewrites in parallel.

        Parameters
        ----------
        state : dict
            Workflow state containing 'questions'.

        Returns
        -------
        dict
            {'query_classification': {0: [...], 1: [...], 2: [...]}}
        """
        levels = [0,1,2]
        results = {}

        def classify(level):
            try:
                result = self.query_classification(state, level)
                return level, result
            except Exception as e:
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
        """
        Classify a query into one or more legal categories.

        Parameters
        ----------
        state : dict
            Workflow state containing 'questions'.
        level : int
            Which query variant to classify.

        Returns
        -------
        dict
            {'query_classification': {level: [query_text, index_keys]}}
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
                        indexes += ["gdpr_index_recall_retriever","gdpr_index_precision_retriever"]
                    if category == 'Greek Penal Code':
                        indexes += ["gpc_index_recall_retriever","gpc_index_precision_retriever"]
                    if category == 'Specific Legal Cases':
                        indexes += ["law_cases_index_recall_retriever","law_cases_index_precision_retriever"]
                    if category == 'Phishing Scenarios':
                        indexes += ["phishing_retriever"]
                state['query_classification'] = {level:[state['questions'][level],indexes]}
            else: state['query_classification'] = {level:[state['questions'][level],None]}

        except Exception as e:
            state['query_classification'] = {level:[state['questions'][level],None]}

        return {'query_classification':state['query_classification']}
    
    def run_retrievals_parallel(self, state):
        """
        Retrieve documents for each query variant in parallel.

        Parameters
        ----------
        state : dict
            Workflow state with classifications.

        Returns
        -------
        dict
            {'retrieved_docs': {0: [...], 1: [...], 2: [...]}}
        """
        levels = [0,1,2]
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


    def retrieve_docs(self, state, level: int):
        """
        Retrieve docs for a single query variant.

        Parameters
        ----------
        state : dict
            Workflow state with classifications.
        level : int
            Which query variant to process.

        Returns
        -------
        list | None
            List of [doc_text, metadata, score] or None if no indexes found.
        """
        retrieved_documents = self.retrieving_docs(state['questions'][0],self.index_mapping,state['query_classification'][level][1],self.reranker_model,self.cohere_client) if state['query_classification'][level][1] else None
        return retrieved_documents
    
    def get_context(self, state):
        """
        Summarize retrieved documents into a coherent context.

        Parameters
        ----------
        state : dict
            Workflow state containing 'retrieved_docs' and 'questions'.

        Behavior
        --------
        - Iterates through retrieval results for each query variant (0,1,2).
        - Summarizes each batch of retrieved documents via the LLM.
        - Concatenates summaries into a single combined context.

        Returns
        -------
        dict
            {'summarized_context': str} – the aggregated context string.
        """
        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        def summarize_level(level:int):
            if not state['retrieved_docs'][level]:
                return level, ""
            retrieved_documents = state['retrieved_docs'][level][level]
            if len(retrieved_documents) == 0:
                return level, ""
            
            joined_context = '\n'.join(f'{i}) {retrieved_documents[i][0]} (score:{retrieved_documents[i][2]}) metadata:{retrieved_documents[i][1]}' for i in range(len(retrieved_documents)))

            response = self.model.invoke(summarized_prompt.format(
                query=state['questions'][level],
                summarized_context=joined_context
            ))

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
    
    def get_search_results(self, query: str):
        """
        Perform Tavily web search and summarize results.

        Parameters
        ----------
        query : str
            User query in English.

        Returns
        -------
        dict
            {'search_results': str} – summarized context from Tavily results.
        """
        search_tool = TavilySearch(
            max_results=5,
            include_answer=True,
            include_raw_content=True,
            include_images=False,
            tavily_api_key=settings.TAVILY_API_KEY,
        )

        search_results = search_tool.invoke({"query": query})

        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        response = self.model.invoke(summarized_prompt.format(
            query=query,
            summarized_context='\n'.join(f'{result["title"]} (score:{result["score"]}) url:{result["url"]} content:{result["content"]}' for result in search_results)
        ))

        summarized_context = str(response.content).strip()
        return {'search_results': summarized_context}

    def initialize_workflow(self):
        """
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

        Returns
        -------
        StateGraph
            Compiled LangGraph app with MemorySaver checkpointing.
        """
        workflow = StateGraph(AgentState)

        ## Query re-writing
        workflow.add_node('query_rewriting',self.query_rewriting)
        ## Query Categorization of query and variants
        workflow.add_node('parallel_classification',self.run_classifications_parallel)
        ## Document Retrieval
        workflow.add_node('parallel_retrieval',self.run_retrievals_parallel)
        ## Document Aggregation and Response
        workflow.add_node("get_context",self.get_context)

        ## Query re-writing -> Query Categorization
        workflow.add_edge("query_rewriting","parallel_classification")
        # ## Query Categorization -> Retrieval Documents
        workflow.add_edge("parallel_classification","parallel_retrieval")
        # ## Retrieval Documents -> Document Aggregation and Response
        workflow.add_edge("parallel_retrieval","get_context")

        workflow.set_entry_point("query_rewriting")
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer = checkpointer)

        return app
    
    def run_full_pipeline(self, query: str):
        """
        Execute the full RAG workflow for a user query.

        Steps
        -----
        1. starting_prompt → checks safety & domain.
        2. query_translation → ensures English query.
        3. Run web_search + rag_pipeline in parallel.
        4. Aggregate results: legal context + web results.

        Parameters
        ----------
        query : str
            Raw user query (any language).

        Returns
        -------
        dict | str
            If query is legal:
                {
                  "query": translated_query,
                  "summarized_context": str,
                  "search_results": str,
                  "language": str
                }
            If query is non-legal or unsafe:
                str – helpful or refusal message.
        """
        start_time = time.time()
        
        res = self.starting_prompt(query)
        if res[0] == True:
            language, translated_query = self.query_translation(query)

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_search = executor.submit(self.web_search, translated_query)
                future_rag = executor.submit(self.rag_pipeline, translated_query)

            end_time = time.time()
            print(f"Pipeline execution time: {end_time - start_time:.2f} seconds")
            return {"query":translated_query,
                'summarized_context':future_rag.result()['summarized_context'],
                'search_results':future_search.result()['search_results'],
                "language":language
                }

        else: 
            end_time = time.time()
            print(f"Pipeline execution time: {end_time - start_time:.2f} seconds")
            return res[1]
    
    


    
