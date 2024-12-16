import json
import os
from collections import defaultdict

with open('invertedIdx.json', 'r') as f:
    inverted_idx = json.load(f)
with open('lexicon.json', 'r') as f:
    lexicon = json.load(f)

output_dir = 'aphabetical_barrels'
os.makedirs(output_dir, exist_ok=True)
barrel_data_dict = defaultdict(list)

def get_alphabetical_barrel(word):
    first_letter = word[0].upper()
    if 'A' <= first_letter <= 'C':
        return 'A_C'
    elif 'D' <= first_letter <= 'F':
        return 'D_F'
    elif 'G' <= first_letter <= 'I':
        return 'G_I'
    elif 'J' <= first_letter <= 'L':
        return 'J_L'
    elif 'M' <= first_letter <= 'O':
        return 'M_O'
    elif 'P' <= first_letter <= 'R':
        return 'P_R'
    elif 'S' <= first_letter <= 'U':
        return 'S_U'
    elif 'V' <= first_letter <= 'X':
        return 'V_X'
    else:
        return 'Y_Z'

# Iterate through the inverted index and map each word to a barrel based on its first letter
for word_id, doc_data in inverted_idx.items():
    # Determine the barrel for the word based on its first letter
    barrel_name = get_alphabetical_barrel(word_id)
    
    # Prepare document data to be added to the barrel
    for doc_id, metadata in doc_data.items():
        barrel_data = {
            'word_id': word_id,
            'doc_id': doc_id,
            'url': metadata['URL'],
        }

        # Append the document data to the appropriate barrel
        barrel_data_dict[barrel_name].append(barrel_data)

# Write all the accumulated barrel data to files at once
for barrel_name, data in barrel_data_dict.items():
    file_path = os.path.join(output_dir, f"{barrel_name}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

print(f"Barrels have been saved in the '{output_dir}' directory.")