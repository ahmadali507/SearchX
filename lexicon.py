from flask import Flask, request, jsonify
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
from flask_cors import CORS
from math import log

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define constants
WORD_ID_RANGE = 1000
NUM_THREADS = 4
K1 = 1.5
B = 0.75
ALPHA = 0.7  # Weight for BM25 in combined score

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

# Load document metadata
with open('document_lengths.json', 'r') as f:
    document_lengths = json.load(f)

# Total number of documents
N = len(document_lengths)

# Average document length
avg_doc_length = sum(document_lengths.values()) / N

def process_text(text):
    stop_words = set(stopwords.words('english'))
    punctuation_set = set(string.punctuation)
    tokens = word_tokenize(text.lower())
    processed_tokens = []
    domain_suffixes = [".com", ".org", ".dev", ".gov", ".io", ".edu", ".net", ".js", ".cpp", ".json"]
    
    for token in tokens:
        token = token.replace("'", "")
        if token.startswith(("http", "www", "//")):
            continue
        if token.endswith("'s"):
            token = token[:-2]
        for suffix in domain_suffixes:
            if token.endswith(suffix):
                token = token[:-len(suffix)]
                break
        if not token.isascii():
            continue
        token = token.lstrip('/')
        if '-' in token:
            sub_tokens = token.split('-')
            for sub_token in sub_tokens:
                if sub_token not in stop_words and sub_token not in punctuation_set:
                    processed_tokens.append(sub_token)
        else:
            if token not in stop_words and token not in punctuation_set and len(token) > 1:
                processed_tokens.append(token)
    return processed_tokens

def get_barrel_filename(word_id):
    barrel_id = int(word_id) // WORD_ID_RANGE
    return f'barrels/barrel_{barrel_id}.msgpack'

def load_barrel(barrel_filename):
    if not os.path.exists(barrel_filename):
        return {}
    with open(barrel_filename, 'rb') as f:
        return msgpack.unpackb(f.read(), raw=False)

def calculate_bm25(freq, doc_length, num_docs_with_term):
    """
    Calculate BM25 score for a term in a document.
    """
    idf = log((N - num_docs_with_term + 0.5) / (num_docs_with_term + 0.5) + 1)
    numerator = freq * (K1 + 1)
    denominator = freq + K1 * (1 - B + B * (doc_length / avg_doc_length))
    return idf * (numerator / denominator)

def calculate_proximity_score(positions1, positions2):
    """
    Calculate proximity score based on the minimum distance between two lists of positions.
    """
    min_distance = float('inf')
    for pos1 in positions1:
        for pos2 in positions2:
            distance = abs(pos1 - pos2)
            if distance < min_distance:
                min_distance = distance
    return 1 / (1 + min_distance)  # Higher score for smaller distances

def process_token_batch_with_proximity(tokens, lexicon):
    doc_scores = {}
    barrel_files = {}
    
    for token in tokens:
        if token not in lexicon:
            continue
        word_id = str(lexicon[token])
        barrel_filename = get_barrel_filename(word_id)
        if barrel_filename not in barrel_files:
            barrel_files[barrel_filename] = []
        barrel_files[barrel_filename].append(word_id)
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        barrels = {
            filename: executor.submit(load_barrel, filename) for filename in barrel_files.keys()
        }
    
    for barrel_filename, word_ids in barrel_files.items():
        barrel_data = barrels[barrel_filename].result()
        for word_id in word_ids:
            if word_id not in barrel_data:
                continue
            documents = barrel_data[word_id]
            for doc_id, doc_data in documents.items():
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {
                        'freq': {},
                        'density': 0,
                        'tokens': set(),
                        'positions': {}
                    }
                doc_scores[doc_id]['freq'][word_id] = doc_data['freq']
                doc_scores[doc_id]['density'] += doc_data['density']
                doc_scores[doc_id]['tokens'].add(word_id)
                doc_scores[doc_id]['positions'][word_id] = doc_data['positions']
    
    # Calculate BM25 and proximity scores
    for doc_id, score_data in doc_scores.items():
        doc_length = document_lengths.get(doc_id, avg_doc_length)
        bm25_score = 0
        for word_id, freq in score_data['freq'].items():
            bm25_score += calculate_bm25(freq, doc_length, len(score_data['tokens']))
        score_data['bm25_score'] = bm25_score
        
        if len(score_data['tokens']) > 1:  # Only consider proximity if multiple tokens match
            proximity_score = 0
            tokens = list(score_data['tokens'])
            for i in range(len(tokens)):
                for j in range(i + 1, len(tokens)):
                    positions1 = score_data['positions'][tokens[i]]
                    positions2 = score_data['positions'][tokens[j]]
                    proximity_score += calculate_proximity_score(positions1, positions2)
            score_data['proximity_score'] = proximity_score
        else:
            score_data['proximity_score'] = 0  # No proximity for single token matches

    return doc_scores

def multi_word_search(query, file_path='repositories.csv', top_n=1000):
    start_time = time.time()
    
    tokens = process_text(query)
    process_end = time.time()
    print(f'time taken to process the query into tokens {(process_end-start_time)*1000} ms')
    
    if not tokens:
        print("No valid tokens found in the query.")
        return []
    
    doc_scores = process_token_batch_with_proximity(tokens, lexicon)
    results = []
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file, quotechar='"', delimiter=',', skipinitialspace=True)
        csv_rows = list(csv_reader)
        
        for doc_id, score_data in doc_scores.items():
            try:
                row = csv_rows[int(doc_id)]
                if len(row) >= 8:
                    name = row[0].strip()
                    description = row[1].strip()
                    stars = int(row[4]) if row[4].isdigit() else 0
                    forks = int(row[5]) if row[5].isdigit() else 0
                    watchers = int(row[7]) if row[7].isdigit() else 0
                    url = row[2].strip()
                    final_score = ALPHA * score_data['bm25_score'] + (1 - ALPHA) * score_data['proximity_score']
                    
                    results.append({
                        'doc_id': doc_id,
                        'final_score': final_score,
                        'name': name,
                        'watchers': watchers,
                        'description': description,
                        'stars': stars,
                        'forks': forks,
                        'url': url
                    })
            except (IndexError, ValueError) as e:
                print(f"Error accessing document ID {doc_id}: {e}")
    
    results = sorted(results, key=lambda x: x['final_score'], reverse=True)
    end_time = time.time()
    search_time = end_time - start_time
    print(f"Search completed in {search_time:.4f} seconds.")
    
    return results[:top_n]

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    print('received data', data)
    query = data.get('query', '')
    print(query)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    results = multi_word_search(query)
    if not results:
        return jsonify({'message': 'No results found', 'results': []}), 200
    print(results[0])
    return jsonify({'message': 'Search successful', 'results': results}), 200

if __name__ == '__main__':
    app.run(debug=True)
