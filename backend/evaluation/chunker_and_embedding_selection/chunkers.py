import tiktoken
from chunking_evaluation import BaseChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import re
from chunking_evaluation.chunking import (
    ClusterSemanticChunker,
    LLMSemanticChunker,
    FixedTokenChunker,
    RecursiveTokenChunker,
    KamradtModifiedChunker
)
from chromadb.utils import embedding_functions
import os

encoding = tiktoken.get_encoding('cl100k_base')

def num_tokens(text):
    return len(encoding.encode(text))

class SentenceChunker(BaseChunker):
    def __init__(self,sentences_per_chunk:int=3):
        self.sentences_per_chunk = sentences_per_chunk
        self.max_tokens = 8191
    
    def split_text(self,text:str) -> List[str]:
        if not text: return []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        for i in range(0,len(sentences),self.sentences_per_chunk):
            chunk = ' '.join(sentences[i:i + self.sentences_per_chunk])
            chunks.append(chunk)

        for c in chunks:
            if num_tokens(c) > self.max_tokens: raise ValueError("chunk bigger than max tokens")

        valid_chunks = [c for c in chunks if isinstance(c,str) and c.strip()]
        if not valid_chunks: raise ValueError("No valid string chunks to embed.")

        return valid_chunks
    
class CharacterChunker(BaseChunker):
    def __init__(self,characters_per_chunk:int = 1000, overlap:int = 0):
        self.characters_per_chunk = characters_per_chunk
        self.overlap = overlap

    def split_text(self,text:str) -> List[str]:
        if not text: return []
        chunks = []
        start = 0
        while start < len(text): 
            end = start + self.characters_per_chunk
            if end > len(text): end = len(text)
            chunk = text[start:chunk]
            chunks.append(chunk)
            start += self.characters_per_chunk - self.overlap
        return chunks
        
class TokenChunker(BaseChunker):
    def __init__(self,tokens_per_chunk:int=1000,overlap:int=0,encoding:str='cl100k_base'):
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap = overlap
        self.encoding = encoding
    
    def split_text(self,text:str) -> List[str]:
        fixed_token_chunker = FixedTokenChunker(
            chunk_size = self.tokens_per_chunk,
            chunk_overlap=self.overlap,
            encoding_name=self.encoding
        )
        return fixed_token_chunker.split_text(text)
    
class RecursiveCharacterChunker(BaseChunker):
    def __init__(self,characters_per_chunk:int=1000,overlap:int=0):
        self.characters_per_chunk = characters_per_chunk
        self.overlap = overlap
    
    def split_text(self,text:str) -> List[str]:
        recursive_token_chunker = RecursiveCharacterTextSplitter(
            chunk_size = self.characters_per_chunk,
            chunk_overlap = self.overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )
        return recursive_token_chunker.split_text(text)
    
class ResTokenChunker(BaseChunker):
    def __init__(self,tokens_per_chunk:int=1000,overlap:int=0,encoding:str='cl100k_base'):
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap = overlap
        self.encoding = encoding

    def split_text(self,text:str) -> List[str]:
        recursive_token_chunker = RecursiveTokenChunker(
            chunk_size = self.tokens_per_chunk,
            chunk_overlap = self.overlap,
            separators = ["\n\n", "\n", ".", "?", "!", " ", ""]
        )
        return recursive_token_chunker.split_text(text)
      
class KamradtChunker(BaseChunker):
    def __init__(self,avg_chunk_size:int=500,min_chunk_size:int=50,model:str='cl100k_base',embedding_model:str='text-embedding-3-small'):
        self.avg_chunk_size = avg_chunk_size
        self.min_chunk_size = min_chunk_size
        self.model = model
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key = os.environ['OPENAI_API_KEY'],model_name=embedding_model)

    def count_tokens(self,text) -> int:
        encoder = tiktoken.get_encoding(self.model)
        return len(encoder.encode(text))

    def split_text(self,text:str) -> List[str]:
        kamradt_modified_chunker = KamradtModifiedChunker(
            avg_chunk_size = self.avg_chunk_size,
            min_chunk_size = self.min_chunk_size,
            embedding_function = self.embedding_function,
            length_function = self.count_tokens
        )

        kamradt_chunks = kamradt_modified_chunker.split_text(text)
        return kamradt_chunks
    
class ClusterChunker(BaseChunker):
    def __init__(self,chunk_size:int=500,embedding_model:str='text-embedding-3-small'):
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=os.environ["OPENAI_API_KEY"], model_name=embedding_model)
        self.max_chunk_size = chunk_size

    def openai_token_count(self,string:str) -> int:
        encoding = tiktoken.get_encoding('cl100k_base')
        num_tokens = len(encoding.encode(string,disallowed_special=()))
        return num_tokens
    
    def split_text(self,text:str) -> List[int]:
        cluster_chunker = ClusterSemanticChunker(
            embedding_function = self.embedding_function,
            max_chunk_size=self.max_chunk_size,
            length_function=self.openai_token_count
        )
        return cluster_chunker.split_text(text)
    
class LLMChunker(BaseChunker):
    def __init__(self,model:str = 'gpt-3.5-turbo'):
        self.model = model
    
    def split_text(self,text:str):
        llm_chunker = LLMSemanticChunker(
            organisation='openai',
            model_name = self.model,
            api_key = os.environ["OPENAI_API_KEY"]
        )
        return llm_chunker.split_text(text)
    
