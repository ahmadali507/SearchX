import math
import json
import ast
import string
from collections import defaultdict
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')

lemmatizer = WordNetLemmatizer()

# Load the lexicon
with open('lexicon_data.json', 'r') as f:
    lexicon = json.load(f)

# Function to process text (tokenize and get word positions)
def process_text(text):
    stop_words = set(stopwords.words('english'))
    punctuation_set = set(string.punctuation)
    tokens = word_tokenize(text.lower())
    word_positions = defaultdict(list)

    processed_tokens = []
    domain_suffixes = [".com", ".org", ".dev", ".gov", ".io", ".edu", ".net"]

    for position, token in enumerate(tokens):
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
                word_positions[token].append(position)  # Record the position of the token
    return processed_tokens, word_positions

# Open the output file for writing incrementally
with open('fwdIdx.json', 'w') as output_file:
    output_file.write("{\n")  # Start JSON object
    cumulative_byte_offset = 213  # Initial byte offset, unchanged
    first_doc = True  # Handle commas between entries
    # Load the test CSV for processing
    test_csv = pd.read_csv('repositories.csv')
    with open('repositories.csv', 'r', encoding='utf-8') as f:
        file_content = f.readlines()
        # Process each row in the test CSV
        for idx, row in test_csv.iterrows():
            topics_list = ast.literal_eval(row['Topics'])
            processed_list = ["".join(topic.split()) for topic in topics_list]
            topic = " ".join(processed_list)
            combined_text = f"{row['Name']} {row['Description']} {row['URL']} {row['Language']} {topic}"
            # Calculate byte offset and row length
            doc_start_byte_offset = cumulative_byte_offset
            row_length = len(file_content[idx + 1].encode('utf-8'))  # Includes newline character
             # Default or handle differently  # Includes newline character
            cumulative_byte_offset += row_length + 1  # Update cumulative offset

            # Process the text and get word positions
            tokens, word_positions = process_text(combined_text)

            doc_id = idx + 1  # Use the index as the document ID
            word_data = {}
            total_tokens = len(tokens)
            # Process each token and its positions
            for token, positions in word_positions.items():
                if token in lexicon:
                    word_id = lexicon[token]
                    freq = len(positions)  # Frequency is the length of the positions list
                    density = freq / total_tokens if total_tokens > 0 else 0
                    word_data[word_id] = {
                        "freq": freq,
                        "density": density,
                        "positions": positions  # Store positions of the word in the document
                    }

            # Prepare forward index entry
            forward_entry = {
                "word_data": word_data,
                "byte_offset": [doc_start_byte_offset, row_length]  # Start byte offset and row length
            }

            # Write to the output file incrementally
            if not first_doc:
                output_file.write(",\n")  # Add a comma between entries
            first_doc = False

            # Write the current document's forward index
            output_file.write(f'"{doc_id}": {json.dumps(forward_entry)}')

    output_file.write("\n}\n")  # End JSON object

print("Forward index with byte offsets saved incrementally to 'fwdIdx.json'")
