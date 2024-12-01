import pandas as pd 
import nltk 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import string

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
test_csv = pd.read_csv('test.csv')
lexicon = pd.read_csv('lexicon.csv')
lexicon = dict(zip(lexicon['word_id'], lexicon['word']))

def process_text(text):
    # remove punctuation 
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_token = [
        word for word in tokens
        if word not in stop_words
    ]
    return processed_token

forward_idx = {}


for doc_id , row in test_csv.iterrows():
   combined_text = f"{row['Name']} {row['Description']} {row['URL']} {row['Language']}, {row['Topics']}"
#    print(combined_text)
   tokens = process_text(combined_text)
   word_ids = []
   print(process_text(combined_text))
   for token in tokens: 
       # find the word id from lexicon and add it to word_ids
       for word, word_id in lexicon.items(): 
        #    print(word_id, word)
           if token.lower() == word.lower():
               word_ids.append(word_id)
               break   
   forward_idx[doc_id] = word_ids
   
   f_df = pd.DataFrame(list(forward_idx.items()), columns=['doc_id', 'word_ids'])

# Save to CSV
f_df.to_csv('fwdIdx.csv', index=False)
print("forwerd Idx saved to 'forwardIdx.csv'")