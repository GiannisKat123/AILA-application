import json
import pandas as pd
import random
from openai import OpenAI
from typing import List
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from fuzzywuzzy import fuzz, process
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from backend.database.config.config import settings

class BaseClass:
    def __init__(self,paths:List[str],chunk_size = 1024, chunk_overlap = 512):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.questions_list = []
        self.more_questions_list = []
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.corpora_paths = paths
        self.model = 'gpt-3.5-turbo'

        path = f'{os.getcwd()}//backend//evaluation//'

        with open(path+'creation_of_synthetic_dataset/prompts/another_prompt.txt','r') as f:
            self.four_question_query = f.read()

        with open(path+'creation_of_synthetic_dataset/prompts/question_maker_system.txt', 'r') as f:
            self.question_maker_system_prompt = f.read()

        with open(path+'creation_of_synthetic_dataset/prompts/question_maker_approx_system.txt', 'r') as f:
            self.question_maker_approx_system_prompt = f.read()
        
        with open(path+'creation_of_synthetic_dataset/prompts/question_maker_user.txt', 'r') as f:
            self.question_maker_user_prompt = f.read()

        with open(path+'creation_of_synthetic_dataset/prompts/question_maker_approx_user.txt', 'r') as f:
            self.question_maker_approx_user_prompt = f.read()

    def generate_queries_and_excerpts(self,approximate_excepts=False,queries_per_corpus=5):
        for corpus_id in self.corpora_paths:
            self._generate_corpus_questions(corpus_id, approx=approximate_excepts, n=queries_per_corpus)

    def find_query_despite_whitespace(self,document, query):
        # Normalize spaces and newlines in the query
        normalized_query = re.sub(r'\s+', ' ', query).strip()
        
        # Create a regex pattern from the normalized query to match any whitespace characters between words
        pattern = r'\s*'.join(re.escape(word) for word in normalized_query.split())
        
        # Compile the regex to ignore case and search for it in the document
        regex = re.compile(pattern, re.IGNORECASE)
        match = regex.search(document)
        
        if match:
            return document[match.start(): match.end()], match.start(), match.end()
        else:
            return None

    def rigorous_document_search(self,document: str, target: str):
        """
        This function performs a rigorous search of a target string within a document. 
        It handles issues related to whitespace, changes in grammar, and other minor text alterations.
        The function first checks for an exact match of the target in the document. 
        If no exact match is found, it performs a raw search that accounts for variations in whitespace.
        If the raw search also fails, it splits the document into sentences and uses fuzzy matching 
        to find the sentence that best matches the target.
        
        Args:
            document (str): The document in which to search for the target.
            target (str): The string to search for within the document.

        Returns:
            tuple: A tuple containing the best match found in the document, its start index, and its end index.
            If no match is found, returns None.
        """
        if target.endswith('.'):
            target = target[:-1]
        
        if target in document:
            start_index = document.find(target)
            end_index = start_index + len(target)
            return target, start_index, end_index
        else:
            raw_search = self.find_query_despite_whitespace(document, target)
            if raw_search is not None:
                return raw_search

        # Split the text into sentences
        sentences = re.split(r'[.!?]\s*|\n', document)

        # Find the sentence that matches the query best
        best_match = process.extractOne(target, sentences, scorer=fuzz.token_sort_ratio)

        if best_match[1] < 98:
            return None
        
        reference = best_match[0]

        start_index = document.find(reference)
        end_index = start_index + len(reference)

        return reference, start_index, end_index

    def _generate_corpus_questions(self,corpus_id,approx=False,n=5):
        with open(corpus_id, 'r',encoding='utf-8') as file:
            corpus = file.read()
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            length_function = len,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )

        chunks = text_splitter.split_text(corpus)
        print("Chunks: ",len(chunks))
        for corpus_chunk in chunks:
            questions_chunk = []
            i = 0
            while i < n:
                j = 0
                while j<5:
                    try:
                        print(f"Trying Query {i}")
                        if approx:
                            question, references = self._extract_question_and_approx_references(corpus_chunk, 4000, questions_chunk)
                        else:
                            question, references = self._extract_question_and_references(corpus_chunk, 4000, questions_chunk)
                        if len(references) > 5:
                            raise ValueError("The number of references exceeds 5.")
                        
                        references = [{'content': ref[0], 'start_index': ref[1], 'end_index': ref[2]} for ref in references]
                        new_question = {
                            'question': question,
                            'references': json.dumps(references),
                            'corpus_id': corpus_id
                        }

                        self.questions_list.append(new_question)
                        questions_chunk.append(question)
                        break
                    except (ValueError, json.JSONDecodeError) as e:
                        j+=1
                        print(f"Error occurred: {e}")
                        continue
                i += 1

            while True:
                try:
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        response_format={ "type": "json_object" },
                        max_tokens=1500,
                        messages=[
                            {"role": "system", "content": self.four_question_query},
                            {"role": "user", "content": self.question_maker_approx_user_prompt.replace("{document}", corpus_chunk)}
                        ]
                    )
                    
                    json_response = json.loads(completion.choices[0].message.content)

                    print(json_response)

                    for data in json_response['questions']:
                        print(data.keys())
                        self.more_questions_list.append([data['question'],data['location'],corpus_id])
                    break
                except Exception as e:
                    continue

    def _tag_text(self, text):
        chunk_length = 100
        chunks = []
        tag_indexes = [0]
        start = 0
        while start < len(text):
            end = start + chunk_length
            chunk = text[start:end]
            if end < len(text):
                # Find the last space within the chunk to avoid splitting a word
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    end = start + space_index + 1  # Include the space in the chunk
                    chunk = text[start:end]
            chunks.append(chunk)
            tag_indexes.append(end)
            start = end  # Move start to end to continue splitting

        tagged_text = ""
        for i, chunk in enumerate(chunks):
            tagged_text += f"<start_chunk_{i}>" + chunk + f"<end_chunk_{i}>"

        return tagged_text, tag_indexes

    def save_questions(self,path:str,filename:str = 'synthetic_data'):
        data = [[query['question'],str(query['references']), query['corpus_id']] for query in self.questions_list]
        df = pd.DataFrame(data, columns = ['question','references','corpus_id'])
        print(df)
        df.to_csv(f'{path}/{filename}.csv')

        df1 = pd.DataFrame(self.more_questions_list,columns=['question','location','corpus_id'])
        print(df1)
        df1.to_csv(f'{path}/more_{filename}.csv')

    def _extract_question_and_approx_references(self, corpus, document_length=4000, prev_questions=[]):
        if len(corpus) > document_length:
            start_index = random.randint(0, len(corpus) - document_length)
            document = corpus[start_index : start_index + document_length]
        else:
            start_index = 0
            document = corpus
        
        if prev_questions is not None:
            if len(prev_questions) > 20:
                questions_sample = random.sample(prev_questions, 20)
                prev_questions_str = '\n'.join(questions_sample)
            else:
                prev_questions_str = '\n'.join(prev_questions)
        else:
            prev_questions_str = ""

        tagged_text, tag_indexes = self._tag_text(document)

        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={ "type": "json_object" },
            max_tokens=600,
            messages=[
                {"role": "system", "content": self.question_maker_approx_system_prompt},
                {"role": "user", "content": self.question_maker_approx_user_prompt.replace("{document}", tagged_text).replace("{prev_questions_str}", prev_questions_str)}
            ]
        )
        
        json_response = json.loads(completion.choices[0].message.content)
        
        try:
            text_references = json_response['references']
        except KeyError:
            raise ValueError("The response does not contain a 'references' field.")
        try:
            question = json_response['question']
        except KeyError:
            raise ValueError("The response does not contain a 'question' field.")

        references = []
        for reference in text_references:
            reference_keys = list(reference.keys())

            if len(reference_keys) != 3:
                raise ValueError(f"Each reference must have exactly 3 keys: 'content', 'start_chunk', and 'end_chunk'. Got keys: {reference_keys}")

            if 'start_chunk' not in reference_keys or 'end_chunk' not in reference_keys:
                raise ValueError("Each reference must contain 'start_chunk' and 'end_chunk' keys.")

            if 'end_chunk' not in reference_keys:
                reference_keys.remove('content')
                reference_keys.remove('start_chunk')
                end_chunk_key = reference_keys[0]
                end_index = start_index + tag_indexes[reference[end_chunk_key]+1]
            else:
                end_index = start_index + tag_indexes[reference['end_chunk']+1]

            start_index = start_index + tag_indexes[reference['start_chunk']]
            references.append((corpus[start_index:end_index], start_index, end_index))
        
        return question, references

    def _extract_question_and_references(self, corpus, document_length=4000, prev_questions=[]):
        if len(corpus) > document_length:
            start_index = random.randint(0, len(corpus) - document_length)
            document = corpus[start_index : start_index + document_length]
        else:
            document = corpus
        
        if prev_questions is not None:
            if len(prev_questions) > 20:
                questions_sample = random.sample(prev_questions, 20)
                prev_questions_str = '\n'.join(questions_sample)
            else:
                prev_questions_str = '\n'.join(prev_questions)
        else:
            prev_questions_str = ""

        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={ "type": "json_object" },
            max_tokens=600,
            messages=[
                {"role": "system", "content": self.question_maker_system_prompt},
                {"role": "user", "content": self.question_maker_user_prompt.replace("{document}", document).replace("{prev_questions_str}", prev_questions_str)}
            ]
        )
        
        json_response = json.loads(completion.choices[0].message.content)
        
        try:
            text_references = json_response['references']
        except KeyError:
            raise ValueError("The response does not contain a 'references' field.")
        try:
            question = json_response['question']
        except KeyError:
            raise ValueError("The response does not contain a 'question' field.")

        references = []
        for reference in text_references:
            if not isinstance(reference, str):
                raise ValueError(f"Expected reference to be of type str, but got {type(reference).__name__}")
            target = self.rigorous_document_search(corpus, reference)
            if target is not None:
                reference, start_index, end_index = target
                references.append((reference, start_index, end_index))
            else:
                raise ValueError(f"No match found in the document for the given reference.\nReference: {reference}")
        
        return question, references

