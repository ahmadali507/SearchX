import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import json

# # Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

# Load inverted index and lexicon
with open('invertedIdx.json', 'r') as f:
    inverted_index = json.load(f)
with open('lexicon.json', 'r') as f:
    lexicon = json.load(f)
test_csv = pd.read_csv('test.csv')
test_csv = test_csv.set_index(test_csv.index).to_dict(orient='index')

# Function to preprocess text
def process_query(search_text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(search_text.lower())
    processed_tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and word not in string.punctuation
    ]
    return processed_tokens

# Search function based on the new structure
def search(search_text):
    specific_tokens = process_query(search_text)
    print(f"Processed Query Tokens: {specific_tokens}")
    
    # Convert tokens into word IDs using the lexicon
    word_ids = [lexicon[token] for token in specific_tokens if token in lexicon]
    print(lexicon['cpp'])
    print(f"Word IDs: {word_ids}")
    
    results = {}
    
    # Iterate through the word IDs in the inverted index
    for word_id in word_ids:
        word_id_str = str(word_id)  # Convert to string to match keys in inverted index
        if word_id_str in inverted_index:
            # Iterate through documents containing the word
            for doc_id, doc_data in inverted_index[word_id_str].items():
                if doc_id not in results:
                    # Add document to results if not already present
                    results[doc_id] = {
                        'Name' : test_csv[int(doc_id)]['Name'],
                        'Description' : test_csv[int(doc_id)]['Description'],
                        'doc_id': doc_id,
                        'score': 0,
                        'stars': doc_data['stars'],
                        'forks': doc_data['forks'],
                        'url': doc_data['URL'],
                        'issues': doc_data['Issues'],
                        'Languages' : test_csv[int(doc_id)]['Language'],
                        'Topics' : test_csv[int(doc_id)]['Topics']
                        # 'has_downloads': doc_data['Has_downloads']
                    }
                # Update the score based on frequency and density
                results[doc_id]['score'] += doc_data['freq'] + (doc_data['density'] * 10)
    
    # print(f"Raw Results: {results}")
    
    # Sort results by score, stars, and forks (in descending order)
    ranked_results = sorted(
        results.values(),
        key=lambda x: (x['score'], x['stars'], x['forks']),
        reverse=True
    )
    
    # Return top N results
    top_n = 100
    return ranked_results[:top_n]

# Example query
query = "LEETCODE PROBLEM SOLVING"
search_results = search(query)

# Display results
for result in search_results:
    print(f"Name: {result['Name']}, Description: {result['Description']}, Stars: {result['stars']}, Forks: {result['forks']}, URL: {result['url']}, Languages: {result['Languages']}, Topics: {result['Topics']}")
    print('\n')