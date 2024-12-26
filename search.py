import csv
import msgpack
import os
import json
import nltk
import time
from concurrent.futures import ThreadPoolExecutor
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Define constants
WORD_ID_RANGE = 1000
NUM_THREADS = 4  # Number of threads for multithreading

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the lexicon
with open('lexicon_data.json', 'r') as f:
    start_time = time.time()
    lexicon = json.load(f)
    end_time = time.time()
    print(f'time taken in loading lexicon + {(end_time-start_time)*1000} + seconds') 

# Preprocess text to handle queries
def process_text(text):
    # Predefine stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    punctuation_set = set(string.punctuation)
    tokens = word_tokenize(text.lower())
    # Process tokens
    processed_tokens = []
    domain_suffixes = [".com", ".org", ".dev", ".gov", ".io", ".edu", ".net",".js", ".cpp", ".json",]
    for token in tokens:
        token = token.replace("'", "")
        # if there is any link token somewhere skip it inside the document text. 
        if token.startswith(("http", "www", "//")):
            continue
        # if tokens are possessive convert them back to simple. 
        if token.endswith("'s"):
            token = token[:-2]
        # removed words that contain any domain names... like freecodecamp.org ... common in github repo description. 
        for suffix in domain_suffixes: 
            if token.endswith(suffix): 
                token = token[:-len(suffix)]
                break
        if not token.isascii():
            continue 
        # Remove leading slashes
        token = token.lstrip('/')
        # Handle hyphenated words: split into individual words
        if '-' in token:
            sub_tokens = token.split('-')
            for sub_token in sub_tokens:
                if sub_token not in stop_words and sub_token not in punctuation_set:
                    processed_tokens.append(sub_token)
        else:
            # Filter out stopwords, punctuation, and single-character tokens
            if token not in stop_words and token not in punctuation_set and len(token) > 1:
                processed_tokens.append(token)
    return processed_tokens

# Determine the barrel filename for a given word ID
def get_barrel_filename(word_id):
    """
    Get the filename of the barrel containing the given word ID.
    """
    barrel_id = int(word_id) // WORD_ID_RANGE
    return f'barrels/barrel_{barrel_id}.msgpack'

# Load a single barrel file using MessagePack
def load_barrel(barrel_filename):
    """
    Load a barrel file stored in MessagePack format.
    """
    if not os.path.exists(barrel_filename):
        return {}
    with open(barrel_filename, 'rb') as f:
        return msgpack.unpackb(f.read(), raw=False)

# Function to process a batch of tokens and retrieve documents
def process_token_batch(tokens, lexicon):
    """
    Process a batch of tokens and retrieve relevant documents from barrels.
    """
    doc_scores = {}
    barrel_files = {}
    
    # Group tokens by barrel
    for token in tokens:
        if token not in lexicon:
            continue
        word_id = str(lexicon[token])  # Convert to string for consistency
        barrel_filename = get_barrel_filename(word_id)
        if barrel_filename not in barrel_files:
            barrel_files[barrel_filename] = []
        barrel_files[barrel_filename].append(word_id)
    
    # Load barrels concurrently
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        barrels = {
            filename: executor.submit(load_barrel, filename) for filename in barrel_files.keys()
        }
    
    # Process results after barrels are loaded
    for barrel_filename, word_ids in barrel_files.items():
        barrel_data = barrels[barrel_filename].result()
        for word_id in word_ids:
            if word_id not in barrel_data:
                continue
            documents = barrel_data[word_id]
            for doc_id, doc_data in documents.items():
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {
                        'freq': 0,
                        'density': 0,
                        'tokens': set()
                    }
                # Aggregate scores and track tokens present
                doc_scores[doc_id]['freq'] += doc_data['freq']
                doc_scores[doc_id]['density'] += doc_data['density']
                doc_scores[doc_id]['tokens'].add(token)
    
    return doc_scores

# Optimized multi-word search function
def multi_word_search(query, file_path='repositories.csv', top_n=1000):
    """
    Perform a search for multi-word queries using barrel-based indexing and multithreading.

    Parameters:
        query (str): The search query (single or multiple words).
        file_path (str): Path to the dataset file.
        top_n (int): Number of top results to return.

    Returns:
        list: List of search results with relevant information.
    """
    # Start timing the search
    start_time = time.time()
    
    # Preprocess the query
    
    
    tokens = process_text(query)
    
    process_end = time.time()
    print(f'time taken to process the query into tokens {(process_end-start_time)*1000} ms')
    if not tokens:
        print("No valid tokens found in the query.")
        return []
    
    # Retrieve documents for all tokens
    
    
    
    doc_scores = process_token_batch(tokens, lexicon)
    
    # Read dataset and fetch document details using byte offsets
    results = []
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file, quotechar='"', delimiter=',', skipinitialspace=True)
        csv_rows = list(csv_reader)  # Read all rows to avoid seeking for every doc
        
        for doc_id, score_data in doc_scores.items():
            # Skip documents that don't contain all query tokens
            if len(score_data['tokens']) < len(tokens):
                continue
            
            # Parse document details using doc_id as index
            try:
                row = csv_rows[int(doc_id)]
                if len(row) >= 8:  # Ensure enough fields exist
                    name = row[0].strip()
                    description = row[1].strip()
                    stars = int(row[4]) if row[4].isdigit() else 0
                    forks = int(row[5]) if row[5].isdigit() else 0
                    url = row[2].strip()
                    
                    # Append the result
                    results.append({
                        'doc_id': doc_id,
                        'freq': score_data['freq'],  # Aggregated frequency
                        'density': score_data['density'],  # Aggregated density
                        'name': name,
                        'description': description,
                        'stars': stars,
                        'forks': forks,
                        'url': url
                    })
            except (IndexError, ValueError) as e:
                print(f"Error accessing document ID {doc_id}: {e}")
    
    # Sort results by relevance (e.g., frequency or density)
    results = sorted(results, key=lambda x: (x['freq'], x['density']), reverse=True)
    
    # Stop timing the search
    end_time = time.time()
    search_time = end_time - start_time
    
    print(f"Search completed in {search_time:.4f} seconds.")
    return results[:top_n]  # Return only the top_n results

# Example usage
if __name__ == "__main__":
    query = input("Enter your search query (single or multiple words): ").strip()
    results = multi_word_search(query, file_path='repositories.csv', top_n=15)
    
    if results:
        for result in results:
            print(f"Doc ID: {result['doc_id']}, Frequency: {result['freq']}, Density: {result['density']}")
            print(f"Name: {result['name']}, Description: {result['description']}")
            print(f"Stars: {result['stars']}, Forks: {result['forks']}, URL: {result['url']}")
            print("-" * 50)
    else:
        print("No results found for the query.")
