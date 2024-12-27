import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import string
import json
import ast

# Download necessary NLTK data
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

test_csv = pd.read_csv('repositories.csv')
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(tag):
    """ Map POS tags from nltk to wordnet format. """
    if tag.startswith('J'):
        return wordnet.ADJ 
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

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

# Initialize lexicon dictionary
lexicon = {}
curr_id = 1

# Iterate through rows to build lexicon
for index, row in test_csv.iterrows():
    # Combine text fields for tokenization
 
    
    topics_list = ast.literal_eval(row['Topics'])
    processed_list = ["".join(topic.split()) for topic in topics_list]
    topic = " ".join(processed_list)
    
    
    
    combined_text = f"{row.get('Name', '')} {row.get('Description', '')} {row.get('Language', '')} {topic}"

    # Process the combined text
    tokens = process_text(combined_text)
    # Get POS tags for tokens
    pos_tags = nltk.pos_tag(tokens)
    for token, pos_tag in pos_tags:
        # Get the wordnet POS tag based on the nltk POS tag
        wordnet_pos = get_wordnet_pos(pos_tag)
        
        # Apply lemmatization based on the POS tag
        lemmatized_token = lemmatizer.lemmatize(token, pos = wordnet_pos)
        
        # Add the lemmatized word as key and assign a unique ID if not already present
        if lemmatized_token not in lexicon:
            lexicon[lemmatized_token] = curr_id
            curr_id += 1

# Save lexicon as JSON
with open('lexicon_data.json', 'w') as f:
    json.dump(lexicon, f, indent=4)

print("Optimized lexicon saved to 'lexicon_data.json'")