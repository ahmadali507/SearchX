import math
import json

# Load forward index
with open('fwdidx.json', 'r') as f:
    forward_idx = json.load(f)

total_docs = len(forward_idx)
with open('inverted_index.json', 'w') as output_file:
    output_file.write("{\n")  # Start of JSON object

    first_word = True  
    
    word_doc_data = {}
    for doc_id, doc_data in forward_idx.items():
        byte_offset = doc_data.get("byte_offset")
        word_data = doc_data.get("word_data")

        for word_id, metadata in word_data.items():
            if word_id not in word_doc_data:
                word_doc_data[word_id] = []
            word_doc_data[word_id].append({
                "doc_id": doc_id,
                "freq": metadata["freq"],
                "density": metadata["density"],
                "byte_offset": byte_offset,
                "positions": metadata["positions"]
            })

    for word_id, doc_data in word_doc_data.items():
        if not first_word:
            output_file.write(",\n")  # Add a comma between word entries
        first_word = False

        postings_list = {}
        for entry in doc_data:
            doc_id = entry["doc_id"]
            postings_list[doc_id] = {
                "freq": entry["freq"],
                "density": entry["density"],
                "byte_offset": entry["byte_offset"],
                "positions": entry["positions"]
            }

        output_file.write(f"\"{word_id}\": {json.dumps(postings_list, indent=4)}")
    output_file.write("\n}\n")

print("Inverted index saved incrementally to 'inverted_index.json'")
    