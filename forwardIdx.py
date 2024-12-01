import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import json

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

test_csv = pd.read_csv('test.csv')
lexicon_df = pd.read_csv('lexicon.csv')

# first converting file csv data to dict --> Hashmap... 
lexicon = dict(zip(lexicon_df['word'], lexicon_df['word_id']))
def process_text(text):
    # stopwords removal for optimizing tokenizations. 
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_tokens = [
        # lemmatize the word to its base form for improving search results
        lemmatizer.lemmatize(word) for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return processed_tokens

# using Dict to store the forward index data bcz dicts behave as hashmaps in python
forward_idx = {}
for idx, row in test_csv.iterrows():
    # Building the combined text by using only relevant fields from the dataset. 
    combined_text = f"{row['Name']} {row['Description']} {row['URL']} {row['Language']} {row['Topics']}"
    # use the above process_text function to obtain the tokens in each row in thier base form. 
    tokens = process_text(combined_text) 
    doc_id = idx #Using the index of each doc in dataset as doc_id ... 
    # now against each doc_id .. we will store the tuples containg the word_id, frequency, density of that word in doc..
    word_data = {} 
    #word_data contains data of the words occuring in the document. 
    total_tokens = 0
    for token in tokens:
            word_id = lexicon[token] # get the word_id from the lexicon for the word/token. 
            word_data[word_id] = word_data.get(word_id, 0) + 1 # increment the frequency 0th value of tuple of the word in the doc.
            total_tokens += 1
    for word_id in word_data:
        freq = word_data[word_id]
        density = freq / total_tokens if total_tokens > 0 else 0
        word_data[word_id] = (freq, density) # store the frequency and density of the word in the doc against that word_id... 
    # to maintain order we have to use list of dicts instead of dict of dicts... 
    #todos ... imporve the csv design .. to dict of dict while maintaining order.. 
    forward_idx[doc_id] = word_data
    
    
    
with open('fwdIdx.json', 'w') as f:
    json.dump(forward_idx, f, indent=4)
print("Forward index saved to 'fwdIdx.json'")

# f_df = pd.DataFrame(forward_idx)
# f_df.to_csv('fwdIdx.csv', index=False)
# print("Forward index saved to 'fwdIdx.csv'")
