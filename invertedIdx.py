import math
import json
from collections import defaultdict

# Load forward index
with open('fwdIdx.json', 'r') as f:
    forward_idx = json.load(f)

# Total number of documents
total_docs = len(forward_idx)

# Open the output file for writing the inverted index incrementally
with open('inverted_index.json', 'w') as output_file:
    output_file.write("{\n")  # Start of JSON object

    first_word = True  # To handle commas between word entries
    chunk_size = 10000  # Set chunk size (adjust as necessary)
    chunk = defaultdict(list)  # Use defaultdict to group word data

    # Process the forward index to build the inverted index incrementally
    for doc_id, doc_data in forward_idx.items():
        byte_offset = doc_data.get("byte_offset")
        word_data = doc_data.get("word_data")
        
        for word_id, metadata in word_data.items():
            # Group word data by word_id
            chunk[word_id].append({
                "doc_id": doc_id,
                "freq": metadata["freq"],
                "density": metadata["density"],
                "byte_offset": byte_offset,
                "positions": metadata["positions"]
            })
        
        # If we have reached the chunk size, write the current chunk to the file
        if len(chunk) >= chunk_size:
            # Write the current chunk to the output file
            if not first_word:
                output_file.write(",\n")  # Add a comma between word entries
            first_word = False

            # Process each word in the chunk and write it incrementally
            for word_id, doc_data in chunk.items():
                # Compute IDF for the current word
                doc_freq = len(doc_data)
                idf = math.log(total_docs / doc_freq) if doc_freq > 0 else 0

                # Prepare postings list without sorting and TF-IDF
                postings_list = {}
                for entry in doc_data:
                    doc_id = entry["doc_id"]
                    postings_list[doc_id] = {
                        "freq": entry["freq"],
                        "density": entry["density"],
                        "byte_offset": entry["byte_offset"],
                        "positions": entry["positions"]
                    }

                # Write the word entry to the file in correct JSON format
                word_entry = f'"{word_id}": ' + json.dumps(postings_list, indent=4)
                output_file.write(word_entry)

            # Clear the chunk after writing to the file
            chunk.clear()

    # If there are remaining chunks to write (after the loop finishes)
    if chunk:
        if not first_word:
            output_file.write(",\n")  # Add a comma between word entries
        first_word = False

        # Process the final chunk
        for word_id, doc_data in chunk.items():
            # Compute IDF for the current word
            doc_freq = len(doc_data)
            idf = math.log(total_docs / doc_freq) if doc_freq > 0 else 0

            # Prepare postings list without sorting and TF-IDF
            postings_list = {}
            for entry in doc_data:
                doc_id = entry["doc_id"]
                postings_list[doc_id] = {
                    "freq": entry["freq"],
                    "density": entry["density"],
                    "byte_offset": entry["byte_offset"],
                    "positions": entry["positions"]
                }

            # Write the word entry to the file in correct JSON format
            word_entry = f'"{word_id}": ' + json.dumps(postings_list, indent=4)
            output_file.write(word_entry)

    # End of JSON object
    output_file.write("\n}\n")

print("Inverted index with positions (no sorting, no TF-IDF) saved incrementally to 'inverted_index.json'")