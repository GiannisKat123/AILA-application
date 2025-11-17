from ChunkingEvalRag import BaseClass
import os,sys
import pandas as pd
import ast
from typing import Dict
sys.path.append(os.path.abspath("../../../"))
from backend.database.core.funcs import get_document_themes, get_documents_by_theme


def save_file(document:Dict[str,str],path:str):
    with open(path,'w',encoding='utf-8') as f:
        f.write(document['content'])

path_folder = f'{os.getcwd()}//backend//evaluation//'

def initialize_document_queries():
    if not os.path.exists(f'{path_folder}synthetic_data_new/queries.csv'):
        themes = get_document_themes()
        for theme in themes:
            paths = []
            os.makedirs(f'{path_folder}files//{theme}',exist_ok=True)
            files = get_documents_by_theme(theme=theme)['documents']
            for file in files:
                print(file)
                save_file(file,f'{path_folder}files//{theme}//{file["title"]}')
                paths.append(f'{path_folder}files//{theme}//{file["title"]}')
            base_class = BaseClass(paths)
            base_class.generate_queries_and_excerpts(approximate_excepts=False,queries_per_corpus=5)
            base_class.save_questions(path=f'{path_folder}synthetic_data_new',filename=f'synthetic_data_{theme}')

            df = pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')
            ar = []
            for i in range(len(df)):
                if df['references'][i] == "[]" or (len(ast.literal_eval(df['references'][i])) == 1 and ast.literal_eval(df['references'][i])[0]['content'] == ''): continue
                else: ar.append([df['question'][i],df['references'][i],df['corpus_id'][i]])

            df = pd.DataFrame(ar,columns=['question','references','corpus_id'])
            df.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')

        files = [pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv',index_col=0) for theme in themes if os.path.exists(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')]
        combined_df = pd.concat(files,ignore_index=True)
        combined_df.to_csv(f'{path_folder}synthetic_data_new/queries.csv',index=True)

        files = [pd.read_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv',index_col=0) for theme in themes if os.path.exists(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv')]
        combined_df = pd.concat(files,ignore_index=True)
        combined_df.to_csv(f'{path_folder}synthetic_data_new/more_queries.csv',index=True)

    else:return


def create_queries_on_docs(theme:str=None,doc:Dict[str,str]=None):
    paths = []
    themes = get_document_themes()
    if not os.path.exists(f'{path_folder}synthetic_data_new/queries.csv'): return 
    if theme is not None:
        documents = get_documents_by_theme(theme=theme)['documents']
        for document in documents:
            save_file(document,f'{path_folder}files//{theme}//{document["title"]}')
            paths.append(f'{path_folder}files//{theme}//{document["title"]}')
    if doc is not None:
        title = doc.get('title')
        text = doc.get('content')
        theme = doc.get('theme')
        save_file(title,f'{path_folder}files//{theme}//{title}')
        paths = [f'{path_folder}files//{theme}//{doc["title"]}']

    if len(paths) == 0: return   


    base_class = BaseClass(paths)
    base_class.generate_queries_and_excerpts(approximate_excepts=False,queries_per_corpus=5)
    base_class.save_questions(path=f'{path_folder}synthetic_data_new',filename=f'synthetic_data_{theme}_new')
    
    df = pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}_new.csv')
    
    if os.path.exists(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv'):
        df_new = pd.concat([df,pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')],ignore_index=True)
        df_new.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv',index=True)
    else: 
        df.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv',index=False)


    ar = []
    for i in range(len(df)):
        if df['references'][i] == "[]" or (len(ast.literal_eval(df['references'][i])) == 1 and ast.literal_eval(df['references'][i])[0]['content'] == ''): continue
        else: ar.append([df['question'][i],df['references'][i],df['corpus_id'][i]])

    df = pd.DataFrame(ar,columns=['question','references','corpus_id'])
    df.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}_new.csv')
    
    if os.path.exists(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv'):
        df_new = pd.concat([df,pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')],ignore_index=True)
        df_new.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv',index=True)
    else: df.to_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')

    if os.path.exists(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv'):
        df_new = pd.concat([pd.read_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}_new.csv'),pd.read_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv')],ignore_index=True)
        df_new.to_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv',index=True)
    else: 
        df = pd.read_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}_new.csv')
        df.to_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv',index=False)
    

    files = [pd.read_csv(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv',index_col=0) for theme in themes if os.path.exists(f'{path_folder}synthetic_data_new/synthetic_data_{theme}.csv')]
    combined_df = pd.concat(files,ignore_index=True)
    combined_df.to_csv(f'{path_folder}synthetic_data_new/queries.csv',index=True)

    files = [pd.read_csv(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv',index_col=0) for theme in themes if os.path.exists(f'{path_folder}synthetic_data_new/more_synthetic_data_{theme}.csv')]
    combined_df = pd.concat(files,ignore_index=True)
    combined_df.to_csv(f'{path_folder}synthetic_data_new/more_queries.csv',index=True)

# initialize_document_queries()
create_queries_on_docs(theme='Greek Cybercrime Legislation')