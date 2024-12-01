import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Load the test_data file
test_csv = pd.read_csv('test.csv')

# Initialize the WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# Tokenizing and processing the text data
def process_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_token = [
        word for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return processed_token

# Process each row of the test dataset
lexicon = {}
curr_id = 1

for index, row in test_csv.iterrows():
    combined_text = f"{row['Name']} {row['Description']} {row['URL']} {row['Language']} {row['Topics']}"
    tokens = process_text(combined_text)
    for token in tokens:
        lemmatized_token = lemmatizer.lemmatize(token)
        if lemmatized_token not in lexicon:
            lexicon[lemmatized_token] = {'id': curr_id, 'originals': []}
            curr_id += 1
        
        if token != lemmatized_token and token not in lexicon[lemmatized_token]['originals']:
            lexicon[lemmatized_token]['originals'].append(token)


