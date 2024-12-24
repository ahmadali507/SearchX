import csv
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load necessary files
with open('inverted_index.json', 'r') as f:
    inverted_idx = json.load(f)

with open('lexicon.json', 'r') as f:
    lexicon = json.load(f)

# Preprocess text to handle queries
def process_text(text):
    """
    Preprocess the query text: tokenize, remove stopwords, and punctuation.
    """
    stop_words = set(stopwords.words('english'))
    punctuation_set = set(string.punctuation)
    tokens = word_tokenize(text.lower())
    
    processed_tokens = []
    for token in tokens:
        token = token.replace("'", "")
        if token not in stop_words and token not in punctuation_set and len(token) > 1:
            processed_tokens.append(token)
    return processed_tokens

# Multi-word search function
def multi_word_search(query, file_path='repositories.csv', top_n=1000):
    """
    Perform a search for multi-word queries.

    Parameters:
        query (str): The search query (single or multiple words).
        file_path (str): Path to the dataset file.
        top_n (int): Number of top results to return.

    Returns:
        list: List of search results with relevant information.
    """
    # Preprocess the query
    tokens = process_text(query)
    if not tokens:
        return []
    
    # Retrieve documents for all tokens
    doc_scores = {}
    for token in tokens:
        if token not in lexicon:
            continue  # Skip tokens not in the lexicon
        
        word_id = str(lexicon[token])  # Convert to string to match inverted index keys
        if word_id not in inverted_idx:
            continue  # Skip tokens not in the inverted index
        
        documents = inverted_idx[word_id]
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
    
    # Read dataset and fetch document details using byte offsets
    results = []
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file, quotechar='"')  # Properly parse CSV rows with quoting
        for doc_id, score_data in doc_scores.items():
            # Skip documents that don't contain all query tokens
            if len(score_data['tokens']) < len(tokens):
                continue
            
            # Retrieve document details from byte offset
            byte_offset = inverted_idx[str(lexicon[list(score_data['tokens'])[0]])][doc_id]['byte_offset']
            start, length = byte_offset
            file.seek(start)  # Jump to the document's start position
            doc_content = file.read(length).strip()
            
            # Parse the row using csv.reader
            try:
                row = next(csv.reader([doc_content], quotechar='"'))
                if len(row) >= 8:  # Ensure enough fields exist
                    name = row[0].strip()
                    description = row[1].strip()
                    stars = int(row[6]) if row[6].isdigit() else 0
                    forks = int(row[7]) if row[7].isdigit() else 0
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
            except (csv.Error, StopIteration) as e:
                print(f"Error parsing CSV line: {doc_content}. Error: {e}")
                break
    
    # Sort results by relevance (e.g., frequency or density)
    results = sorted(results, key=lambda x: (x['freq'], x['density']), reverse=True)
    
    return results[:top_n]  # Return only the top_n results

# Example usage
if _name_ == "_main_":
    query = input("Enter your search query (single or multiple words): ").strip()
    results = multi_word_search(query, file_path='repositories.csv', top_n=15)
    
    if results:
        for result in results:
            print(f"Doc ID: {result['doc_id']}, Frequency: {result['freq']}, Density: {result['density']}")
            print(f"Name: {result['name']}, Description: {result['description']}")
            print(f"Stars: {result['stars']}, Forks: {result['forks']}, URL: {result['url']}")
            print("-" * 50)
    else:
        print("No results found for the query.")