import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.database.core.funcs import get_feedback
import pandas as pd
import numpy as np

path = f'{os.getcwd()}//backend//evaluation//synthetic_data_new'

documents_feedback = get_feedback()
ar = [t for t in documents_feedback]
df = pd.DataFrame(ar,columns=['username','query','negative_answer','doc_name','doc_text','context','theme'])
df.to_csv(f'{path}//feedback.csv')

