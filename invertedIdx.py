import pandas as pd
import nltk 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

test_csv = pd.read_csv('test.csv')
fwdIdx_csv = pd.read_csv('fwdIdx.csv')
lexicon_csv = pd.read_csv('lexicon.csv')

# for efficent lookups converting the data from csv in list format to dict .. for efficent hashmap lookups... 
lexicon = dict(zip(lexicon_csv['token'], lexicon_csv['id']))
fwdIdx = dict(zip(fwdIdx_csv['doc_id'], fwdIdx_csv['word_data']))


inverted_idx = {}
# list to store the doc_ids containing that word and the frequency of the word in that doc with density. 

for doc_id, word_data in fwdIdx.items(): 
    # doc_id is the key and word_data is the value in the forward index.
    # here we want the word_id to be key and the doc_data to be the values ... 
    
    for word_id, (freq, density) in word_data.items(): 
        # now saving the word_id and doc_id in the inverted index... 
        
        if word_id not in inverted_idx: 
            inverted_idx[word_id] = {}
        # now we have the word_id in the inverted index..
        # storing the doc_id and frequency and density of word in that doc in inverted index. 
        if doc_id not in inverted_idx[word_id]:
            inverted_idx[word_id][doc_id] = {
                'freq': freq,
                'density': density, 
                'URL' : test_csv.iloc[doc_id]['URL'],
                'stars' : test_csv.iloc[doc_id]['Stars'],
                'forks' : test_csv.iloc[doc_id]['Forks']
                # added stars and forks with doc_id to rank the results based on stars and forks for popularity of the repo
            }
print("Optimized Inverted Index:")
for word_id, doc_data in inverted_idx.items():
    print(f"Word ID {word_id}: {doc_data}")
        



