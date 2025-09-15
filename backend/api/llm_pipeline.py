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

def load_vector_index(top_k:int,persist_dir:str, embedding):
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context=storage_context,embed_model=embedding)
    return index.as_retriever(similarity_top_k=top_k,search_type='hybrid')

def load_reranker_model():
    co = cohere.ClientV2(settings.COHERE_API_KEY)
    ft = co.finetuning.get_finetuned_model(settings.COHERE_MODEL_ID)
    return co,ft

def initialize_indexes(top_k:int):

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
        "law_cases_index_recall_retriever":law_cases_index_recall_retriever,
        "law_cases_index_precision_retriever":law_cases_index_precision_retriever,
        "gpc_index_recall_retriever":gpc_index_recall_retriever,
        "gpc_index_precision_retriever":gpc_index_precision_retriever,
        "gdpr_index_recall_retriever":gdpr_index_recall_retriever,
        "gdpr_index_precision_retriever":gdpr_index_precision_retriever,
    }

class AgentState(TypedDict):
    user_query: str
    summarized_context:str
    search_results: str
    questions: List[str]                    # ✅ Good
    query_classification: Annotated[Dict[str, List[str]], operator.or_]     # ✅ Good
    retrieved_docs: Annotated[Dict[str, List], operator.or_]                # ✅ Good
    context: Annotated[Dict[str, str], operator.or_] 




class LLM_Pipeline():
    def __init__(self,index_mapping:dict[str,VectorIndexRetriever],reranker_model:CrossEncoder|GetFinetunedModelResponse,cohere_client:cohere.ClientV2|None = None):
        self.cohere_client = cohere_client
        self.index_mapping = index_mapping
        self.reranker_model = reranker_model
        self.client = OpenAI(api_key=settings.API_KEY)
        self.model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY, temperature=0.7)
        self.app = self.initialize_workflow()

    def language_detection_query(self, message: str):
        prompt = """Find the language used in the following query: {message}"""
        
        # Match the placeholder name with the keyword argument
        response = self.model.invoke(prompt.format(message=message))
        
        response_content = str(response.content).strip()
        print(response_content)
        language = response_content
        return language

    def retrieving_docs(self,query:str,index_mapping:dict[str,VectorIndexRetriever],indexes:List[VectorIndexRetriever],reranker_model:CrossEncoder|GetFinetunedModelResponse,cohere_client:cohere.client_v2.ClientV2|None):
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

    def starting_prompt(self,conversation_history:List[str],query:str):
        
        print(conversation_history)

        if conversation_history:

            # prompt = """
            # You are a query rewriter for a legal assistant.
            # Using the conversation and most importantly the latest user message, produce ONE standalone question that
            # preserves the same intent and keeps entities/sections exact.
            # - Keep language the same as the user's latest message.
            # - Output ONLY the rewritten question, no quotes, no extra text.

            # Conversation (oldest→newest):
            # {history}

            # Latest user message:
            # {query}

            # Rewritten standalone question:
            # """

            prompt = """
            You are a question rewriter for a legal assistant.

            Your task: Given the conversation history and the user’s new input, rewrite the question so that it is:
            - Fully self-contained: do not use pronouns, ellipses, or vague references.
            - Context-aware: ONLY if the new question is clearly about the SAME legal subject, merge with context.
            - Reset: if the new question is unrelated (greeting, small talk, weather, etc.), IGNORE history COMPLETELY and return the new question as-is.
            - Jurisdiction-aware: restrict scope to Greek Penal Code and GDPR where relevant.
            - Concise: keep the question short, precise, and in the same language as the user.
            - Output strictly one rewritten question and nothing else.

            Conversation summary:
            {history}

            Recent turns:
            {last_turns}

            New question:
            {new_question}

            Rewritten question: 
                -) If the new question is unrelated return the {new_question} 
                -) ELSE your generated answer
            """


            history = [mes['message'] for mes in conversation_history][-10:]

            print(prompt.format(new_question=query,history=history,last_turns= conversation_history[-1]))

            response = self.model.invoke(prompt.format(new_question=query,history=history,last_turns= conversation_history[-1]))
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
        return response_content,query
    
    
    def query_translation(self,query:str):
        lang = self.language_detection_query(query)

        prompt = """
        You are a highly competent legal assistant. Your task is to accurately translate the following legal query into English while preserving its original meaning, legal terminology, and nuance.

        Text to translate:
        {query}

        Provide only the translated version. Do not explain, rephrase, or annotate. 
        """

        response = self.model.invoke(prompt.format(query=query))
        response_content = str(response.content).strip()
        query = response_content

        language = lang
        return language,query
    
    def web_search(self,query:str):
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

        prompt = "You are a highly competent legal assistant. You provide accurate, well-reasoned, and context-aware answers\
                to legal questions specifically related to cybercrime and phishing. Your primary sources are the Greek Penal Code and the GDPR. \
                Always cite relevant articles, explain reasoning clearly, and when uncertain, state the limitations rather than speculate."

        summarized_context = self.client.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )

        return {'search_results': summarized_context.output_text}
    
    def rag_pipeline(self,query:str,app):
        config = {"configurable": {"thread_id": f"{uuid4()}"}}
        result = app.invoke({
            "user_query":query,
            "questions": [],  # <-- ADD THIS
            "query_classification": {},  # <-- FIXED
            "retrieved_docs": {},  # <-- ADD THIS
            "context": {},  # <-- ALREADY GOOD
        }, config)

        return {"query":query,
            'summarized_context':result['summarized_context'],
            }
        
    def query_rewriting(self,state):
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

    def run_classifications_parallel(self,state):
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

    def query_classification(self,state,level:int):
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

            User Query: Πως μου κατι σχετικο με τη νομολογια
            Output: ["Specific Legal Cases"]

            User Query: tell me something about Greek Jurisdiction
            Output: ["Specific Legal Cases"]

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
    
    def run_retrievals_parallel(self,state):
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


    def retrieve_docs(self,state,level):
        retrieved_documents = self.retrieving_docs(state['questions'][0],self.index_mapping,state['query_classification'][level][1],self.reranker_model,self.cohere_client) if state['query_classification'][level][1] else None
        state['retrieved_docs'][level] = retrieved_documents
        return {level:state['retrieved_docs'][level]}
    
    def get_context(self,state):
        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        def summarize_level(level:int):
            if not state['retrieved_docs'][level]:
                return level, ""
            print(state['retrieved_docs'][level])
            retrieved_documents = state['retrieved_docs'][level][level]
            if retrieved_documents == None:  return level, ""
            if len(retrieved_documents) == 0: return level, ""
            
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

    def initialize_workflow(self):

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
    
    def run_full_pipeline(self,query:str,conversation_history:List[str],app,web_search_activation:bool):        
        res,new_query = self.starting_prompt(conversation_history,query)
        print(res,new_query,web_search_activation)
        if res.lower() == 'true':
            language, translated_query = self.query_translation(new_query)

            summarized_content = ''
            if web_search_activation:
                print('ONLINE MODE')
                web_search = self.web_search(translated_query)
                summarized_content = web_search['search_results']
                print(summarized_content)
            else:
                print('RAG MODE')
                rag_search = self.rag_pipeline(translated_query,app)
                summarized_content = rag_search['summarized_context']
                print(summarized_content)

            return {"query":translated_query,
                'summarized_context':summarized_content,
                "language":language
                } 
            
            # with ThreadPoolExecutor(max_workers=2) as executor:
            #     future_search = executor.submit(self.web_search, translated_query)
            #     future_rag = executor.submit(self.rag_pipeline, translated_query,app)

            # return {"query":translated_query,
            #     'summarized_context':future_rag.result()['summarized_context'],
            #     'search_results':future_search.result()['search_results'],
            #     "language":language
            #     }

        else: 
            lang = self.language_detection_query(query)
            prompt = """
            You are a highly competent legal assistant. You answer questions that are non-legal and possibly out of knowledge. 
            
            You goal is to provide a short answer to the user question but always make sure that you make your role known to the user.

            For example:

                If non-legal:  "Helpful, short answer **plus** a clear reminder that you are a legal assistant."
                If the query is inappropriate, illegal, or unsafe: "I'm a legal assistant. I cannot answer unsafe or inappropriate questions."
                If the query does not make sense, help the user.

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
                - Respond in {lang}. However if the question does not make sense answer in English for good measure.

            User Query: {query}
            """

            response = self.model.invoke(prompt.format(query=new_query,lang=lang))
            response_content = str(response.content).strip()
            return response_content
    