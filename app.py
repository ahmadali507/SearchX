from flask import Flask, request, jsonify
from flask_cors import CORS
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
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import heapq
import ast

app = Flask(__name__)
CORS(app)

# Constants
WORD_ID_RANGE = 1000
BARRELS_SIZE = 120
NUM_THREADS = 4
CACHE_SIZE = 1000

# Initialize NLTK
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

# Load data at startup
def load_offset_index():
    try:
        with open('barrel_offset_index.msgpack', 'rb') as f:
            return msgpack.unpackb(f.read(), raw=False)
    except FileNotFoundError:
        print("Error: Offset index not found!")
        return {}

offset_index = load_offset_index()
stop_words = set(stopwords.words('english'))
punctuation_set = set(string.punctuation)

with open('lexicon_data.json', 'r') as f:
    lexicon = json.load(f)

# Cache for document data
doc_cache = {}

def read_word_data(word_id: str) -> Dict:
    if word_id not in offset_index:
        return None
        
    location = offset_index[word_id]
    barrel_id = location['barrel_id']
    barrel_filename = f'barrels/barrel_{barrel_id}.msgpack'
    
    try:
        with open(barrel_filename, 'rb') as barrel_file:
            barrel_data = msgpack.unpackb(barrel_file.read(), raw=False)
            return barrel_data.get(word_id, {})
    except Exception as e:
        print(f"Error reading barrel {barrel_id}: {e}")
        return None

def process_text_with_positions(text: str) -> Tuple[List[str], List[int]]:
    tokens = word_tokenize(text.lower())
    processed_tokens = []
    token_positions = []
    domain_suffixes = frozenset([".com", ".org", ".dev", ".gov", ".io", ".edu", ".net", ".js", ".cpp", ".json"])
    
    for index, token in enumerate(tokens):
        token = token.replace("'", "").lstrip('/')
        
        if any((
            not token.isascii(),
            token.startswith(("http", "www", "//")),
            token in stop_words,
            token in punctuation_set,
            len(token) <= 1
        )):
            continue
            
        if token.endswith("'s"):
            token = token[:-2]
        
        for suffix in domain_suffixes:
            if token.endswith(suffix):
                token = token[:-len(suffix)]
                break
                
        if '-' in token:
            sub_tokens = token.split('-')
            valid_subtokens = [st for st in sub_tokens if st not in stop_words and st not in punctuation_set]
            processed_tokens.extend(valid_subtokens)
            token_positions.extend([index] * len(valid_subtokens))
        else:
            processed_tokens.append(token)
            token_positions.append(index)
            
    return processed_tokens, token_positions

def process_token_batch(tokens: List[str], lexicon: Dict[str, str]) -> Dict:
    doc_scores = defaultdict(lambda: {
        'freq': 0,
        'density': 0,
        'position_score': 0,
        'match_count': 0,
        'tokens': set(),
        'positions': [],
        'byte_offset': None
    })

    total_tokens = len(tokens)

    def calculate_position_score(positions: List[int]) -> float:
        """Calculate a position-based score."""
        if not positions:
            return 0
        positions.sort()
        range_positions = positions[-1] - positions[0] + 1
        return len(positions) / range_positions

    def process_token(token):
        if token in lexicon:
            word_id = str(lexicon[token])
            return token, word_id, read_word_data(word_id)
        return None

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        results = list(executor.map(process_token, tokens))

        for result in results:
            if not result:
                continue

            token, word_id, word_data = result
            if not word_data:
                continue

            for doc_id, doc_data in word_data.items():
                doc_scores[doc_id]['freq'] += doc_data['freq']
                doc_scores[doc_id]['density'] += doc_data['density']
                doc_scores[doc_id]['tokens'].add(token)
                doc_scores[doc_id]['positions'].extend(doc_data['positions'])
                doc_scores[doc_id]['match_count'] += 1
                if doc_scores[doc_id]['byte_offset'] is None:
                    doc_scores[doc_id]['byte_offset'] = doc_data['byte_offset']

    # Normalize frequency and density for fair weighting
    max_freq = max(score['freq'] for score in doc_scores.values())
    max_density = max(score['density'] for score in doc_scores.values())

    for doc_id, score in doc_scores.items():
        coverage = score['match_count'] / total_tokens

        score['position_score'] = calculate_position_score(score['positions'])
        normalized_freq = score['freq'] / max_freq if max_freq else 0
        normalized_density = score['density'] / max_density if max_density else 0

        # Final scoring
        score['final_score'] = (
            normalized_density * 0.1 +
            normalized_freq * 0.1 +
            score['position_score'] * 0.4 +
            coverage * 0.4
        )

    # Sort by final_score in descending order
    return dict(sorted(
        doc_scores.items(),
        key=lambda item: item[1]['final_score'],
        reverse=True
    ))
def calculate_score(name_match: int, description_match: int, freq: int, density: int, alpha=0.4, beta=0.5, gamma=0.1):
    """Scoring function for ranking documents."""
    return alpha * name_match + beta * description_match + gamma * (freq + density)

def paginated_search(query: str, page: int, per_page: int, file_path: str = 'repositories.csv') -> Tuple[List[Dict], float, int, Dict]:
    start = time.perf_counter()
    
    if not query or not isinstance(query, str):
        return [], 0, 0, {}
        
    if not os.path.exists(file_path):
        return [], 0, 0, {}
    
    query_tokens, _ = process_text_with_positions(query)
    if not query_tokens:
        return [], 0, 0, {}
    
    doc_scores = process_token_batch(query_tokens, lexicon)
    # print("QUERY SCORES" , doc_scores)
    if not doc_scores:
        return [], 0, 0, {}
    
    total_results = len(doc_scores)
    start_idx = min((page - 1) * per_page, total_results)
    end_idx = min(start_idx + per_page, total_results)
    print("START AND END IDX", start_idx, end_idx)
    top_docs = dict(list(doc_scores.items())[start_idx : (end_idx)])
    print("Length fo top_docs", len(top_docs))
    heap = []
    results = []
    
    with open(file_path, 'rb') as file:
        for doc_id, score_data in top_docs.items():
            try:
                offset, length = score_data.get('byte_offset', (0, 0))
                file.seek(offset)
                row = next(csv.reader(
                    [file.read(length).decode('utf-8', errors='ignore').strip()],
                    quotechar='"', delimiter=',', skipinitialspace=True
                ))
                
                # Calculate name and description match scores
                name = row[0].strip().lower()
                description = row[1].strip().lower()
                name_match = sum(1 for token in query_tokens if token in name)
                description_match = sum(1 for token in query_tokens if token in description)
                
                # Compute final score
                final_score = calculate_score(
                    name_match=name_match,
                    description_match=description_match,
                    freq=score_data['freq'],
                    density=score_data['density']
                )
                
                # Push document to the max-heap
                heapq.heappush(heap, (-final_score, doc_id, {
                    'doc_id': doc_id,
                    'name': row[0].strip(),
                    'description': row[1].strip(),
                    'url': row[2].strip(),
                    'watchers': int(row[7]) if row[7].isdigit() else 0,
                    'language': row[8] if row[8] else "",
                    'Topics': ast.literal_eval(row[9] if row[9] else "[]"),
                    'stars': int(row[4]) if row[4].isdigit() else 0,
                    'forks': int(row[5]) if row[5].isdigit() else 0,
                    'freq': score_data['freq'],
                    'density': score_data['density'],
                    'final_score': -final_score  # Negated to maintain original value
                }))
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
    
    # Extract top results based on the heap
    top_results = [heapq.heappop(heap)[2] for _ in range(min(len(heap), per_page))]
    search_time = (time.perf_counter() - start) * 1000
    return top_results, search_time, total_results

@app.route('/search', methods=['POST'])
def search():
    try:
        print("hello")
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided', 'status': 400}), 400
        
        query = data['query']
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 10))
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Invalid pagination parameters', 'status': 400}), 400
        
        
        results, search_time, total_count = paginated_search(
            query,
            page=page,
            per_page=per_page,
            file_path='repositories.csv'
        )
        print(search_time)
        return jsonify({
            'status': 200,
            'results': results,
            'search_time_ms': round(search_time, 2),
            'total_count': total_count,
            'current_page': page,
            'per_page': per_page,
            'total_pages': -(-total_count // per_page),
            'query': query
        })
        
        
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 500}), 500
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'cache_size': len(doc_cache)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)