import os
import msgpack
from collections import defaultdict
import json

BARRELS_TOTAL = 120

def create_offset_index():
    offset_index = {}
    
    # Iterate through each barrel file
    for barrel_id in range(BARRELS_TOTAL):
        barrel_filename = f'barrels/barrel_{barrel_id}.msgpack'
        
        if not os.path.exists(barrel_filename):
            continue
            
        # Read and store the starting position for each word_id in the barrel
        with open(barrel_filename, 'rb') as barrel_file:
            barrel_data = msgpack.unpackb(barrel_file.read(), raw=False)
            
            # Store barrel location for each word_id
            for word_id in barrel_data:
                offset_index[word_id] = {
                    'barrel_id': barrel_id
                }
    
    # Save the offset index using MessagePack
    with open('barrel_offset_index.msgpack', 'wb') as f:
        packed_index = msgpack.packb(offset_index, use_bin_type=True)
        f.write(packed_index)
    
    print(f"Created offset index with {len(offset_index)} entries")
    return offset_index

def read_word_data(word_id, offset_index):
    """
    Read specific word data using the offset index
    """
    if word_id not in offset_index:
        return None
        
    location = offset_index[word_id]
    barrel_id = location['barrel_id']
    barrel_filename = f'barrels/barrel_{barrel_id}.msgpack'
    
    with open(barrel_filename, 'rb') as barrel_file:
        barrel_data = msgpack.unpackb(barrel_file.read(), raw=False)
        return {word_id: barrel_data.get(word_id)}

def load_offset_index():
    """
    Load the offset index from file
    """
    try:
        with open('barrel_offset_index.msgpack', 'rb') as f:
            return msgpack.unpackb(f.read(), raw=False)
    except FileNotFoundError:
        print("Offset index not found. Creating new index...")
        return create_offset_index()

# Create or load the offset index
offset_index = load_offset_index()

# Example usage:
if offset_index:
    # Get a sample word_id from the offset index
    sample_word_id = next(iter(offset_index))
    print(f"\nTesting with word_id: {sample_word_id}")
    
    # Read data for the sample word
    word_data = read_word_data(sample_word_id, offset_index)
    print(f"Retrieved data: {word_data}")

    # Test with a specific word_id
    test_word_id = "120"  # or any other word_id you want to test
    print(f"\nTesting with specific word_id: {test_word_id}")
    if test_word_id in offset_index:
        word_data = read_word_data(test_word_id, offset_index)
        print(f"Retrieved data: {word_data}")
    else:
        print(f"Word ID {test_word_id} not found in index")