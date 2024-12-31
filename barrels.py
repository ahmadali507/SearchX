import os
import msgpack
from collections import defaultdict
import json

# Define the word ID range for each barrel
WORD_ID_RANGE = 1000
BARRELS_TOTAL = 120
# Load inverted index
with open('inverted_index.json', 'r') as f:
    inverted_idx = json.load(f)

# Create a directory for barrels
os.makedirs('barrels', exist_ok=True)

# use hashing to assign coreect barrels to the docs...
barrel_data = defaultdict(dict)
for word_id, doc_data in inverted_idx.items():

    barrel_id = int(word_id) % BARRELS_TOTAL
    barrel_data[barrel_id][word_id] = doc_data
    
# Save each barrel using MessagePack
for barrel_id, words in barrel_data.items():
    barrel_filename = f'barrels/barrel_{barrel_id}.msgpack'
    with open(barrel_filename, 'wb') as barrel_file:
        packed_data = msgpack.packb(words, use_bin_type=True)
        barrel_file.write(packed_data)
    print(f'Barrel {barrel_id} saved to {barrel_filename}')

print("Barrels have been created using MessagePack for faster serialization.")
