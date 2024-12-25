import json
import os
from collections import defaultdict

BARRELS_SIZE = 15000 
with open('inverted_index.json', 'r') as f:
    inverted_idx = json.load(f)

os.makedirs('barrels', exist_ok=True)
chunk = defaultdict(dict)
barrel_count = 0
current_size = 0
for word_id, doc_data in inverted_idx.items():
    chunk[word_id] = doc_data
    current_size += len(doc_data)  
    # fi we create barrels based on number fo word_ids per barrels then barrels arre not equally sized 
    # so we use documents per barrels .. like number of barrels to limit the barrels size for equally sized barrels.
    if current_size >= BARRELS_SIZE:
        barrel_count += 1
        barrel_filename = f'barrels/barrel_{barrel_count}.json'
        with open(barrel_filename, 'w') as barrel_file:
            json.dump(chunk, barrel_file, indent=4)

        print(f'Barrel {barrel_count} saved to {barrel_filename}')

        chunk = defaultdict(dict)
        current_size = 0
if chunk:
    barrel_count += 1
    barrel_filename = f'barrels/barrel_{barrel_count}.json'
    with open(barrel_filename, 'w') as barrel_file:
        json.dump(chunk, barrel_file, indent=4)
    print(f'Final barrel {barrel_count} saved to {barrel_filename}')
print("Barrels have been created and balanced.")