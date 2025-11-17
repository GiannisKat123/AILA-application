from sentence_transformers import CrossEncoder, SentenceTransformer
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.base.base_retriever import BaseRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Dict,TypedDict,List,Annotated
from openai import OpenAI
from langchain_openai import ChatOpenAI
from backend.database.config.config import settings
from backend.database.daos.prompt_dao import PromptDao
from langchain_core.documents.base import Document
from openai.cli._errors import OpenAIError
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator, uuid, ast
from sqlalchemy.orm import Session 
from backend.database.core.funcs import get_prompt

def load_vector_index(top_k:int,persist_dict:str,embedding:HuggingFaceEmbeddings) -> BaseRetriever:
    storage_context = StorageContext.from_defaults(persist_dir=persist_dict)
    index = load_index_from_storage(storage_context=storage_context,embed_model=embedding)
    return index.as_retriever(similarity_top_k=top_k, search_type='hybrid')

def load_reranker_model() -> CrossEncoder:
    reranker_model = CrossEncoder('./backend/cached_reranker_models/IoannisKat1__bge-reranker-basefinetuned-new')
    return reranker_model

def initialize_indexes(top_k:int) -> Dict[str,BaseRetriever]:
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
    user_query:str
    summarized_context:str
    saerch_results:str
    questions:List[str]
    query_classification:Annotated[Dict[str,List[str]],operator.or_]
    retrieved_docs:Annotated[Dict[str,List],operator.or_]
    context:Annotated[Dict[str,str],operator.or_]

class LLM_Pipeline():
    def __init__(self,index_mapping:dict[str,BaseRetriever],reranker_model:CrossEncoder,top_k:int):
        self.index_mapping = index_mapping
        self.reranker_model = reranker_model
        self.top_k = top_k
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.OPENAI_API_KEY,temperature=0.7)
        self.app = self.initialize_workflow()

    def language_detection_query(self,message:str):
        prompt = get_prompt(prompt_name='language_detection')
        response = self.model.invoke(prompt.format(message=message))
        language = str(response.content).strip()
        return language
    
    def retrieving_docs(self,query:str,indexes:List[BaseRetriever]):
        retrieved_nodes = []
        for index in indexes:
            index = self.index_mapping[index]
            nodes = index.retrieve(query)
            retrieved_nodes.append([Document(page_content=node.text,metadata=node.metadata) for node in nodes])
        
        documents = []
        for index_nodes in retrieved_nodes:
            documents += [node for node in index_nodes]
        pairs = [(query, doc.page_content) for doc in documents]
        print("RETRIEVING DOCS",retrieved_nodes,pairs)
        scores = self.reranker_model.predict(pairs)
        scored_docs = list(zip(scores,documents))
        scored_docs.sort(reverse=True,key=lambda x:x[0])
        reranked_docs = scored_docs[:self.top_k]
        return [[node.page_content,node.metadata,float(score)] for score,node in reranked_docs]
    
    def starting_prompt(self,conversation_history:List[str],query:str):
        if conversation_history:
            prompt = get_prompt(prompt_name='query_rewritter_conversation_history')
            history = [mes['message'] for mes in conversation_history][-10:]
            response = self.model.invoke(prompt.format(new_question=query,history=history,last_turns=conversation_history[-1]))
            query = str(response.content).strip()
        prompt = get_prompt(prompt_name='query_classifier')
        response = self.model.invoke(prompt.format(query=query))
        return str(response.content).strip(),query
    
    def query_translation(self,query:str):
        language = self.language_detection_query(query)
        prompt = get_prompt(prompt_name='query_translation_to_english')
        response = self.model.invoke(prompt.format(query=query))
        query = str(response.content).strip()
        return language,query
    
    def web_search(self,query:str):
        prompt = get_prompt(prompt_name='online_search')
        summarized_context = self.client.responses.create(
            model="gpt-4o-mini-2024-07-18",
            tools=[{"type": "web_search_preview"}],
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )

        return {'search_results':summarized_context.output_text}
    
    def rag_pipeline(self,query:str,app):
        config = {"configurable": {"thread_id": f"{uuid.uuid4()}"}}
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
        prompt = get_prompt(prompt_name='query_rewritter')

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
        prompt = get_prompt(prompt_name='query_classification_on_index')
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
        retrieved_documents = self.retrieving_docs(state['questions'][0],state['query_classification'][level][1]) if state['query_classification'][level][1] else None
        state['retrieved_docs'][level] = retrieved_documents
        return {level:state['retrieved_docs'][level]}
    
    def get_context(self,state):
        summarized_prompt = get_prompt(prompt_name='retrieval_summarization')

        def summarize_level(level:int):
            if not state['retrieved_docs'][level]:
                return level, ""
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
        """
        Build and compile the LangGraph workflow:

            query_rewriting → parallel_classification → parallel_retrieval → get_context

        Returns:
            Any: Compiled app instance with an in-memory checkpointer.
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
    
    def run_full_pipeline(self,query:str,conversation_history:List[str],app,web_search_activation:bool):   
        print("REQUEST",query,conversation_history,web_search_activation)
        res,new_query = self.starting_prompt(conversation_history,query)
        if res.lower() == 'true':
            language, translated_query = self.query_translation(new_query)

            summarized_content = ''
            if web_search_activation:
                web_search = self.web_search(translated_query)
                summarized_content = web_search['search_results']
            else:
                rag_search = self.rag_pipeline(translated_query,app)
                summarized_content = rag_search['summarized_context']

            return {"query":translated_query,
                'summarized_context':summarized_content,
                "language":language
                } 

        else: 
            lang = self.language_detection_query(query)
            prompt = get_prompt(prompt_name='safe_non_legal_answer')
            response = self.model.invoke(prompt.format(query=new_query,lang=lang))
            return str(response.content).strip()
    
            