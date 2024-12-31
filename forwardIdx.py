import json
import string
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

with open('lexicon_data.json', 'r') as f:
    lexicon = json.load(f)

def process_text(text):
    stop_words = set(stopwords.words('english'))
    punctuation_set = set(string.punctuation)
    tokens = word_tokenize(text.lower())
    word_positions = defaultdict(list)
    processed_tokens = []

    for position, token in enumerate(tokens):
        token = token.replace("'", "")
        if token.startswith(("http", "www", "//")):
            continue
        if token.endswith("'s"):
            token = token[:-2]
            
        if not token.isascii():
            continue
        token = token.lstrip('/')
        
        if '-' in token:
            sub_tokens = token.split('-')
            for sub_token in sub_tokens:
                if sub_token not in stop_words and sub_token not in punctuation_set:
                    processed_tokens.append(sub_token)
                    word_positions[sub_token].append(position)
        else:
            if token not in stop_words and token not in punctuation_set and len(token) > 1:
                processed_tokens.append(token)
                word_positions[token].append(position)
    return processed_tokens, word_positions

def calculate_byte_offsets():
    offsets = []
    cumulative_offset = 0
    
    with open('repositories.csv', 'rb') as f:
        header = f.readline()
        cumulative_offset = len(header)
        
        while True:
            start_pos = cumulative_offset
            line = f.readline()
            if not line:
                break
            line_length = len(line)
            offsets.append((start_pos, line_length))
            cumulative_offset += line_length
            
    return offsets

byte_offsets = calculate_byte_offsets()

with open('fwdIdx.json', 'w') as output_file:
    output_file.write("{\n")
    first_doc = True

    with open('repositories.csv', 'r', encoding='utf-8') as csv_file:
        next(csv_file)  # Skip header
        for idx, row in enumerate(csv.reader(csv_file)):
            if len(row) < 10: continue
            
            try:
                name = row[0]
                description = row[1]
                combined_text = f"{name} {description}"
                
                tokens, word_positions = process_text(combined_text)
                
                doc_id = idx + 1
                word_data = {}
                total_tokens = len(tokens)

                for token, positions in word_positions.items():
                    if token in lexicon:
                        word_id = lexicon[token]
                        freq = len(positions)
                        density = freq / total_tokens if total_tokens > 0 else 0
                        word_data[word_id] = {
                            "freq": freq,
                            "density": density,
                            "positions": positions
                        }

                if not first_doc:
                    output_file.write(",\n")
                first_doc = False

                output_file.write(f'"{doc_id}": {{"word_data": {json.dumps(word_data)}, '
                                f'"byte_offset": {json.dumps(byte_offsets[idx])}}}')

            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue

    output_file.write("\n}\n")