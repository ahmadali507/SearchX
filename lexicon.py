import pandas as pd 
import nltk
from nltk.tokenize import word_tokenizer
from nltk.corpus import stopwords


test_csv = pd.read_csv('test.csv')
