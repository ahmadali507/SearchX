import pandas as pd 
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import string

nltk.download()
nltk.download('punkt')
nltk.download('stopwords')



#loading the test_data file here.... 
test_csv = pd.read_csv('test.csv')

# tokenizing the test data file here.. .

def process_text(text):
    # remove punctuation 
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_token = [
        word for word in tokens
        if word not in stop_words and word not in string.punctutation
    ]
    return processed_token


# now processign each row of the test data set here ... 

lexicon = {}
curr_id = 1

for index, row in test_csv.iterrows():
    combined_text = f"{row['Name']} {row['Description']} {row['URL']} {row['Language']} {row['Topics']}"
    tokens = process_text(combined_text)
    # lexicon should only contain the unique words .. not nothing else ... 
    for token in tokens:
        if token not in lexicon:
            lexicon[token] = curr_id
            curr_id += 1
            
            
print("Lexcion", lexicon)

lexicon_df = pd.DataFrame(list(lexicon.items()), columns=['word_id', 'word'])

# Save to CSV
lexicon_df.to_csv('lexicon.csv', index=False)
print("Lexicon saved to 'lexicon.csv'")