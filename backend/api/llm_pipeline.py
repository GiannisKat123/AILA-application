import os 
from backend.database.config.config import settings
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import load_index_from_storage
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from llama_index.core.retrievers import VectorIndexRetriever
from typing import Annotated, List, Dict, TypedDict, Tuple
import cohere, ast
from cohere.finetuning.finetuning.types.get_finetuned_model_response import GetFinetunedModelResponse
from langdetect import detect
from langchain.prompts import PromptTemplate 
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from uuid import uuid4
import operator 
from openai.cli._errors import OpenAIError
from langchain.vectorstores import FAISS
from langchain_core.documents.base import Document as langchainDocument
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_tavily import TavilySearch
import tiktoken
import re
from chunking_evaluation import BaseChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chunking_evaluation.chunking import (
    FixedTokenChunker,
    RecursiveTokenChunker,
)
from concurrent.futures import ThreadPoolExecutor, as_completed


def num_tokens(text,encoding):
    return len(encoding.encode(text))

class SentenceChunker(BaseChunker):
    def __init__(self, sentences_per_chunk, encoding):
        # Initialize the chunker with the number of sentences per chunk
        self.sentences_per_chunk = sentences_per_chunk
        self.encoding = encoding

    def split_text(self,text:str) -> List[str]:
        # Handle the case where the input text is empty
        if not text:
            return ""
        
        # Split the input text into sentences using regular expression
        # Regex looks for white space following . ! or ? and makes a split
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []

        for i in range(0, len(sentences), self.sentences_per_chunk):
            # Combine sentences into a single chunk
            chunk = ' '.join(sentences[i:i + self.sentences_per_chunk])
            chunks.append(chunk)
        
        valid_chunks = [c for c in chunks if isinstance(c, str) and c.strip()]
        if not valid_chunks:
            raise ValueError("No valid string chunks to embed.")
        
        MAX_TOKENS = 8191
        for c in chunks:
            if num_tokens(c,self.encoding) > MAX_TOKENS:
                raise ValueError("Bigger than max tokens.")
        # valid_chunks = [c for c in chunks if isinstance(c, str) and c.strip() and num_tokens(c) >= MAX_TOKENS]
        # Return the list of chunks
        return valid_chunks

class CharacterChunker(BaseChunker):
    def __init__(self, characters_per_chunk: int = 1000, overlap: int = 0):
        # Initialize the chunker with the number of characters per chunk
        self.characters_per_chunk = characters_per_chunk
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        # Handle the case where the input text is empty
        if not text:
            indexes += []

        # Initialize an empty list to hold the chunks
        chunks = []
        start = 0

        # Loop to create chunks of specified character length
        while start < len(text):
            end = start + self.characters_per_chunk
            
            # If the end exceeds the text length, adjust it
            if end > len(text):
                end = len(text)

            # Extract the chunk and append it to the list
            chunk = text[start:end]
            chunks.append(chunk)

            # Move the start index forward, considering overlap
            start += self.characters_per_chunk - self.overlap
        
        # Return the list of chunks
        return chunks

class TokenChunker(BaseChunker):
    def __init__(self, tokens_per_chunk: int = 1000, overlap: int = 0, encoding: str = 'cl100k_base'):
        # Initialize the chunker with the number of tokens per chunk
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap = overlap
        self.encoding = encoding

    def split_text(self, text: str) -> List[str]:
        fixed_token_chunker = FixedTokenChunker(
            chunk_size=self.tokens_per_chunk, 
            chunk_overlap=self.overlap,
            encoding_name=self.encoding
        )

        token_chunks = fixed_token_chunker.split_text(text)

        return token_chunks

class RecursiveCharacterChunker(BaseChunker):
    def __init__(self, characters_per_chunk: int = 1000, overlap: int = 0):
        # Initialize the chunker with the number of characters per chunk
        self.characters_per_chunk = characters_per_chunk
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        recursive_token_chunker = RecursiveCharacterTextSplitter(
            chunk_size=self.characters_per_chunk,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""] # According to Research
        )

        recursive_chunks = recursive_token_chunker.split_text(text)

        return recursive_chunks

class ResTokenChunker(BaseChunker):
    def __init__(self, tokens_per_chunk: int = 1000, overlap: int = 0, encoding: str = 'cl100k_base'):
        # Initialize the chunker with the number of tokens per chunk
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap = overlap
        self.encoding = encoding

    def split_text(self, text: str) -> List[str]:
        recursive_token_chunker = RecursiveTokenChunker(
            chunk_size=self.tokens_per_chunk, 
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )

        recursive_chunks = recursive_token_chunker.split_text(text)

        return recursive_chunks


def parse_phishing(file_directory:str,chunker:BaseChunker):
    files = os.listdir(file_directory)
    chunks = []
    counter = 0
    for file in files:
        with open(file_directory + f'/{file}','r',encoding='utf-8') as f:
            text = f.read()
        
        attack_type = file.split('.txt')[0]

        text_chunks = chunker.split_text(text)
        for chunk in text_chunks:
            chunks.append(
                {
                    "id": f"phishing_{counter}",
                    "content": chunk,
                    "metadata": {
                        "source": "Phishing Scenarios",
                        "doc_type": "explainer",
                        "title": attack_type,
                        "lang": "en",
                    }
                }
            )
            counter+=1

    return chunks



def parse_gdpr(file_directory:str,chunker:BaseChunker):
    files = os.listdir(file_directory)
    chunks = []
    counter = 0
    for file in files:
        with open(file_directory + f'/{file}','r',encoding='utf-8') as f:
            text = f.read()
        
        title = file.split('.txt')[0]

        text_chunks = chunker.split_text(text)
        for chunk in text_chunks:
            chunks.append(
                {
                    "id": f"gdpr_{counter}",
                    "content": chunk,
                    "metadata": {
                        "source": "GDPR",
                        "doc_type": "regulation",
                        "title": title,
                        "lang": "en"
                    }
                }
            )   
            counter+=1

    return chunks

def parse_law_cases(file_directory:str,chunker:BaseChunker):
    files = os.listdir(file_directory)
    chunks = []
    counter = 0
    case_id_ = 0
    for file in files:
        with open(file_directory + f'/{file}','r',encoding='utf-8') as f:
            case = f.read()

        match = re.search(r"Decision number:\s*(.*?)\n", case)
        case_id = match.group(1).strip() if match else f"case_{case_id_}"
        court = re.search(r"Court \(Civil/Criminal\):\s*(.*?)\n", case)
        court_type = court.group(1).strip().lower() if court else "unknown"
        outcome = re.search(r"Outcome \(innocent, guilty\):\s*(.*?)\n", case)
        laws = re.findall(r"Law\s+\d+/\d+|Article\s+\d+[A-Z]?(\s+of\s+Law\s+\d+/\d+)?", case)
        
        title = file.split('.txt')[0]

        text_chunks = chunker.split_text(case)
        for chunk in text_chunks:
            chunks.append({
                "id": f"case_{counter}",
                "content": chunk,
                "metadata": {
                    "title":title,
                    "source": "Greek Court Decisions",
                    "doc_type": "case_law",
                    "jurisdiction": "GR",
                    "case_id": case_id,
                    "civil_or_criminal": court_type,
                    "outcome": outcome.group(1).strip() if outcome else "unknown",
                    "relevant_laws": list(set(laws)),
                    "lang": "en"
                }
            })
            counter+=1
        case_id_ +=1 

    return chunks

def parse_cybercrime(file_directory:str,chunker:BaseChunker):
    files = os.listdir(file_directory)
    chunks = []
    counter = 0
    for file in files:
        with open(file_directory + f'/{file}','r',encoding='utf-8') as f:
            text = f.read()
        
        title = file.split('.txt')[0]
        article_id = re.findall(r"Article\s+(\d+[A-Z]?)", title)
        law_id = re.findall(r"[ΝΠΚ]\.?\s?\d+/?\d*", title)

        text_chunks = chunker.split_text(text)
        for chunk in text_chunks:
            chunks.append({
                "id": f"cybercrime_{counter}",
                "content": chunk,
                "metadata": {
                    "title":title,
                    "source": "Greek Cybercrime Law",
                    "doc_type": "criminal_statute",
                    "law": law_id[0] if law_id else "unknown",
                    "article_number": article_id[0] if article_id else str(counter),
                    "lang": "en",
                    "jurisdiction": "GR"
                }
            })
            counter+=1

    return chunks


# def load_vector_index(top_k:int,persist_dir:str, embedding, bm25_retriever):
#     dense_index = FAISS.load_local(folder_path=persist_dir, embeddings=embedding,allow_dangerous_deserialization=True)
#     dense_retriever = dense_index.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
#     return EnsembleRetriever(
#         retrievers = [dense_retriever,bm25_retriever],
#         weights=[0.7,0.3],
#         unique_docs_by="page_content"
#     )

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
        10,
        "./backend/vector_indexes/phishing_index_documents_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__multilingual-e5-large-legal-matryoshka'),
    )

    # ⚖️ Law Cases – Recall
    law_cases_index_recall_retriever = load_vector_index(
        10,
        "./backend/vector_indexes/law_cases_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )

    # ⚖️ Law Cases – Precision
    law_cases_index_precision_retriever = load_vector_index(
        10,
        "./backend/vector_indexes/law_cases_recall_index_documents_precision_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__bge-m3-legal-matryoshka'),
    )

    # 🇬🇷 Greek Penal Code – Recall
    gpc_index_recall_retriever = load_vector_index(
        10,
        "./backend/vector_indexes/gpc_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__legal-bert-base-uncased-legal-matryoshka'),
    )

    # 🇬🇷 Greek Penal Code – Precision
    gpc_index_precision_retriever = load_vector_index(
        10,
        "./backend/vector_indexes/gpc_recall_index_documents_precision_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )


    # 🛡️ GDPR – Recall
    gdpr_index_recall_retriever = load_vector_index(
        10,
        "./backend/vector_indexes/gdpr_recall_index_documents_recall_trained_embedding",
        HuggingFaceEmbeddings(model_name='./backend/cached_embedding_models/IoannisKat1__modernbert-embed-base-legal-matryoshka-2'),
    )

    # 🛡️ GDPR – Precision
    gdpr_index_precision_retriever = load_vector_index(
        10,
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
    language: str
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

    def retrieving_docs(self,query:str,index_mapping:dict[str,VectorIndexRetriever],indexes:List[VectorIndexRetriever],reranker_model:CrossEncoder|GetFinetunedModelResponse,cohere_client:cohere.client_v2.ClientV2|None):
        retrieved_nodes = []
        for index in indexes:
            index = index_mapping[index]
            nodes = index.retrieve(query)
            retrieved_nodes.append([langchainDocument(page_content=node.text,metadata=node.metadata) for node in nodes])

            # nodes = index.get_relevant_documents(query)
            # retrieved_nodes.append(nodes)

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


    def translation_agent(self,state):
        dict_lang = {
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

        lang = detect(state['user_query'])
        if lang != 'en':
            prompt = """
            You are a highly competent legal assistant. Your task is to accurately translate the following legal query into English while preserving its original meaning, legal terminology, and nuance.

            Text to translate:
            {query}

            Provide only the translated version. Do not explain, rephrase, or annotate.
            """

            prompt = PromptTemplate(input_variables=['query'],template=prompt)
            model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,   temperature=0.7 )
            agent_chain = prompt | model

            response = agent_chain.invoke({
                "query":state['user_query']
            })

            response_content = str(response.content).strip()

            state['user_query'] = response_content

        state['language'] = dict_lang[lang]

        return state
    
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
        prompt = PromptTemplate(input_variables=['query'],template=prompt)

        model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,   temperature=0.7 )
        agent_chain = prompt | model

        retries = 3
        for _ in range(retries):
            try:
                response = agent_chain.invoke({
                    "query":state['user_query']
                })

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

            User Query: What is Phishing and give me an example of such case  
            Output: ["Phishing Scenarios", "Specific Legal Cases"]

            Now classify this query:  
            "{query}"

        """
        prompt = PromptTemplate(input_variables=['query'],template=prompt)
        model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,   temperature=0.7 )
        agent_chain = prompt | model

        response = agent_chain.invoke({
            "query":state['questions'][level]
        })

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

    def query_classification_1(self,state):
        return self.query_classification(state,0)

    def query_classification_2(self,state):
        return self.query_classification(state,1)

    def query_classification_3(self,state):
        return self.query_classification(state,2)
    
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
        return retrieved_documents
        # state['retrieved_docs'][level] = retrieved_documents
        # return {level:state['retrieved_docs'][level]}
    
    def retrieve_docs_1(self,state):
        return {'retrieved_docs': self.retrieve_docs(state,0)}

    def retrieve_docs_2(self,state):
        return {'retrieved_docs': self.retrieve_docs(state,1)}

    def retrieve_docs_3(self,state):
        return {'retrieved_docs': self.retrieve_docs(state,2)}

    def get_context(self,state):
        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata.
            
            Context:{summarized_context}

            User Query:{query}
        """

        summarized_prompt = PromptTemplate(input_variables=['query','summarized_context'],template=summarized_prompt)
        model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,   temperature=0.7 )
        agent_chain = summarized_prompt | model

        def summarize_level(level:int):
            if not state['retrieved_docs'][level]:
                return level, ""
            retrieved_documents = state['retrieved_docs'][level]
            if len(retrieved_documents) != 0:
                return level, ""
            
            joined_context = '\n'.join(f'{i}) {retrieved_documents[i][0]} (score:{retrieved_documents[i][2]}) metadata:{retrieved_documents[i][1]}' for i in range(len(retrieved_documents)))

            response = agent_chain.invoke({
                "query":state['user_query'],
                "summarized_context":joined_context
            })

            return level, str(response.content).strip()
        
        summarized_by_level = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(summarize_level, level): level for level in range(3)}
            summarized_contexts = {}
            for future in as_completed(futures):
                level, summary = future.result()
                summarized_contexts[level] = summary

        full_summary = "\n\n".join(
            summarized_by_level[i] for i in range(3) if i in summarized_by_level
        )

        return {'summarized_context': full_summary}
    
    def get_search_results(self,state):
        search_tool = TavilySearch(
            max_results=5,
            include_answer=True,
            include_raw_content=True,
            include_images=False,
            tavily_api_key=settings.TAVILY_API_KEY,
        )

        search_response = search_tool.invoke({"query": state['user_query']})
        

        summarized_prompt = """
            You are a highly competent legal assistant designed to provide accurate, well-reasoned, and context-aware answers to legal questions. Your responses should be clear, concise, and grounded in the provided legal context and conversation history.

            I want you to summarize the following context based on the user query. Keep the most relevant information that can help you answer the user query. Keep also related metadata in the summarized response.
            
            Context:{summarized_context}

            User Query:{query}
        """

        summarized_prompt = PromptTemplate(input_variables=['query','summarized_context'],template=summarized_prompt)
        model = ChatOpenAI(model=settings.OPEN_AI_MODEL,api_key=settings.API_KEY,   temperature=0.7 )
        agent_chain = summarized_prompt | model

        response = agent_chain.invoke({
            "query":state['user_query'],
            "summarized_context":'\n'.join(f"{result['title']}) {result['content']} (score:{result['score']}) metadata:{result['url']}" for result in search_response['results']),
        })

        summarized_context = str(response.content).strip()
        
        return {'search_results': summarized_context}

    def initialize_workflow(self):
        workflow = StateGraph(AgentState)

        ## Query translation
        workflow.add_node("translation",self.translation_agent)
        ## Query re-writing
        workflow.add_node('query_rewriting',self.query_rewriting)

        ## Query Categorization of query and variants
        workflow.add_node('parallel_classification',self.run_classifications_parallel)

        # workflow.add_node("query_categorization_1",self.query_classification_1)
        # workflow.add_node("query_categorization_2",self.query_classification_2)
        # workflow.add_node("query_categorization_3",self.query_classification_3)
        ## Document Retrieval
        workflow.add_node('parallel_retrieval',self.run_retrievals_parallel)
        # workflow.add_node("retrieve_documents_1",self.retrieve_docs_1)
        # workflow.add_node("retrieve_documents_2",self.retrieve_docs_2)
        # workflow.add_node("retrieve_documents_3",self.retrieve_docs_3)
        ## Document Aggregation and Response
        workflow.add_node("get_context",self.get_context)
        ## Search Flow
        workflow.add_node("get_search_results",self.get_search_results)

        ## Query translation -> Query re-writing
        workflow.add_edge("translation","query_rewriting")
        workflow.add_edge("translation","get_search_results")
        ## Query re-writing -> Query Categorization
        workflow.add_edge("query_rewriting","parallel_classification")
        # workflow.add_edge("query_rewriting","query_categorization_1")
        # workflow.add_edge("query_rewriting","query_categorization_2")
        # workflow.add_edge("query_rewriting","query_categorization_3")
        # ## Query Categorization -> Retrieval Documents
        workflow.add_edge("parallel_classification","parallel_retrieval")
        # workflow.add_edge("query_categorization_1","retrieve_documents_1")
        # workflow.add_edge("query_categorization_2","retrieve_documents_2")
        # workflow.add_edge("query_categorization_3","retrieve_documents_3")
        # ## Retrieval Documents -> Document Aggregation and Response
        workflow.add_edge("parallel_retrieval","get_context")
        # workflow.add_edge("retrieve_documents_1","get_context")
        # workflow.add_edge("retrieve_documents_2","get_context")
        # workflow.add_edge("retrieve_documents_3","get_context")
        

        workflow.set_entry_point("translation")
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer = checkpointer)

        return app
    
    def get_context_from_graph(self,app:CompiledStateGraph,user_query:str):
        config = {"configurable": {"thread_id": f"{uuid4()}"}}
        result = app.invoke({
            "language":'',
            "user_query":user_query,
            "questions": [],  # <-- ADD THIS
            "query_classification": {},  # <-- FIXED
            "retrieved_docs": {},  # <-- ADD THIS
            "context": {},  # <-- ALREADY GOOD
        }, config)

        return {"query":user_query,
            'summarized_context':result['summarized_context'],
            'search_results':result['search_results'],
            "language":result['language']
            }
        
    


    
