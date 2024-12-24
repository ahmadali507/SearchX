import math
import json

# Load forward index
with open('fwdIdx.json', 'r') as f:
    forward_idx = json.load(f)

# Total number of documents
total_docs = len(forward_idx)

# Open the output file for writing the inverted index incrementally
with open('inverted_index.json', 'w') as output_file:
    output_file.write("{\n")  # Start of JSON object

    first_word = True  # To handle commas between word entries

    # Process the forward index to build and write the inverted index incrementally
    word_doc_data = {}  # Temporary dictionary to group data by word_id
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

    # Process each word in word_doc_data and write it incrementally
    for word_id, doc_data in word_doc_data.items():
        if not first_word:
            output_file.write(",\n")  # Add a comma between word entries
        first_word = False

        # Compute IDF for the current word
        doc_freq = len(doc_data)
        idf = math.log(total_docs / doc_freq) if doc_freq > 0 else 0

        # Prepare postings list with TF-IDF values
        postings_list = {}
        for entry in doc_data:
            doc_id = entry["doc_id"]
            tf_idf = entry["density"] * idf  # Compute TF-IDF score
            postings_list[doc_id] = {
                "freq": entry["freq"],
                "density": entry["density"],
                "byte_offset": entry["byte_offset"],
                "positions": entry["positions"],
                "tf_idf": tf_idf
            }

        # Sort postings by TF-IDF
        sorted_documents = sorted(postings_list.items(), key=lambda x: x[1]["tf_idf"], reverse=True)

        # Write the word entry to the file in correct JSON format
        word_entry = f'"{word_id}": ' + json.dumps(dict(sorted_documents), indent=4)
        output_file.write(word_entry)

    # End of JSON object
    output_file.write("\n}\n")

print("Inverted index with positions and TF-IDF saved incrementally to 'inverted_index.json'")