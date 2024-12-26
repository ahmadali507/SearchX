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
import math

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Define constants
WORD_ID_RANGE = 1000
NUM_THREADS = 4
k1 = 1.5  # BM25 parameter
b = 0.75  # BM25 parameter

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
    print(f'time taken in loading lexicon: {(end_time - start_time) * 1000} ms')

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

def process_token_batch(tokens, lexicon):
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
                        'freq': 0,
                        'density': 0,
                        'tokens': set()
                    }
                doc_scores[doc_id]['freq'] += doc_data['freq']
                doc_scores[doc_id]['density'] += doc_data['density']
                doc_scores[doc_id]['tokens'].add(token)
    
    return doc_scores

def compute_avg_doc_len(file_path='repositories.csv'):
    total_length = 0
    total_docs = 0
    
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file, quotechar='"', delimiter=',', skipinitialspace=True)
        for row in csv_reader:
            description = row[1].strip() if len(row) >= 8 else ""
            total_length += len(word_tokenize(description.lower()))
            total_docs += 1
    
    return total_length / total_docs if total_docs > 0 else 1

avg_doc_len = compute_avg_doc_len()

def calculate_idf(term, lexicon, barrel_data, total_docs):
    if term not in lexicon:
        return 0
    word_id = str(lexicon[term])
    doc_count = len(barrel_data.get(word_id, {}))
    if doc_count == 0:
        return 0
    return math.log((total_docs - doc_count + 0.5) / (doc_count + 0.5) + 1)

def bm25_score(frequency, doc_len, avg_doc_len, idf):
    numerator = frequency * (k1 + 1)
    denominator = frequency + k1 * (1 - b + b * (doc_len / avg_doc_len))
    return idf * (numerator / denominator)

def multi_word_search(query, file_path='repositories.csv', top_n=1000):
    start_time = time.time()
    
    tokens = process_text(query)
    
    process_end = time.time()
    print(f'Time taken to process the query into tokens: {(process_end - start_time) * 1000} ms')
    if not tokens:
        print("No valid tokens found in the query.")
        return []
    
    doc_scores = process_token_batch(tokens, lexicon)
    
    results = []
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        csv_reader = csv.reader(file, quotechar='"', delimiter=',', skipinitialspace=True)
        csv_rows = list(csv_reader)
        total_docs = len(csv_rows)
        
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
                    
                    bm25 = 0
                    doc_len = len(word_tokenize(description + name))
                    for token in score_data['tokens']:
                        idf = calculate_idf(token, lexicon, score_data, total_docs)
                        frequency = score_data['freq']
                        bm25 += bm25_score(frequency, doc_len, avg_doc_len, idf)
                    
                    results.append({
                        'doc_id': doc_id,
                        'bm25_score': bm25,
                        'freq': score_data['freq'],
                        'density': score_data['density'],
                        'name': name,
                        'description': description,
                        'stars': stars,
                        'forks': forks,
                        'watchers': watchers,
                        'url': url
                    })
            except (IndexError, ValueError) as e:
                print(f"Error accessing document ID {doc_id}: {e}")
    
    results = sorted(results, key=lambda x: x['bm25_score'], reverse=True)
    
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
