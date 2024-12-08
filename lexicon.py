import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import json

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Load the test_data file
test_csv = pd.read_csv('test.csv')
lemmatizer = WordNetLemmatizer()

# Function to preprocess text
def process_text(text):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    processed_tokens = [
        word for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return processed_tokens

# Initialize lexicon dictionary
lexicon = {}
curr_id = 1

# Iterate through rows to build lexicon
for index, row in test_csv.iterrows():
    # Combine text fields for tokenization
    combined_text = f"{row.get('Name', '')} {row.get('Description', '')} {row.get('URL', '')} {row.get('Language', '')} {row.get('Topics', '')}"
    
    # Process the combined text
    tokens = process_text(combined_text)
    for token in tokens:
        lemmatized_token = lemmatizer.lemmatize(token)
        # Add the word as key and assign a unique ID if not already present
        if lemmatized_token not in lexicon:
            lexicon[lemmatized_token] = curr_id
            curr_id += 1

# Save lexicon as JSON
with open('lexicon.json', 'w') as f:
    json.dump(lexicon, f, indent=4)

print("Optimized lexicon saved to 'lexicon.json'")
