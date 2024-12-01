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
test_csv = pd.read_csv('repositories.csv')

lemmatizer = WordNetLemmatizer()

def process_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_tokens = [
        word for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return processed_tokens

lexicon = {}
curr_id = 1
for index, row in test_csv.iterrows():
    combined_text = f"{row.get('Name', '')} {row.get('Description', '')} {row.get('URL', '')} {row.get('Language', '')} {row.get('Topics', '')}"
    
    tokens = process_text(combined_text)
    for token in tokens:
        lemmatized_token = lemmatizer.lemmatize(token)
        if lemmatized_token not in lexicon.values():
            lexicon[curr_id] = lemmatized_token
            curr_id += 1

lexicon_df = pd.DataFrame(list(lexicon.items()), columns=['id', 'token'])
# potential chances of converting to a json based on requirements and efficiency... 
lexicon_df.to_csv('lexicon.csv', index=False)
print("Lexicon saved to 'lexicon.csv'")
