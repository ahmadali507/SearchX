import json
import os
from collections import defaultdict

# Load the inverted index
with open('invertedIdx.json', 'r') as f:
    inverted_idx = json.load(f)

# Define thresholds for frequency, density, and popularity
FREQ_BUCKETS = [1, 3] 
DENSITY_BUCKETS = [0.00, 0.1]  
POPULARITY_BUCKETS = [10000, 70000]

# Folder for barrels
output_dir = 'barrels'
os.makedirs(output_dir, exist_ok=True)

# Use a defaultdict to accumulate barrel data in memory
barrel_data_dict = defaultdict(list)

# Function to calculate the most relevant bucket
def assign_to_single_barrel(total_freq, density, popularity_score):
    # Assign to frequency bucket
    f_bucket = next(f for f, f_next in zip([0] + FREQ_BUCKETS, FREQ_BUCKETS + [float('inf')]) if f <= total_freq < f_next)
    # Assign to density bucket
    d_bucket = next(d for d, d_next in zip([0.0] + DENSITY_BUCKETS, DENSITY_BUCKETS + [float('inf')]) if d <= density < d_next)
    # Assign to popularity bucket
    p_bucket = next(p for p, p_next in zip([0] + POPULARITY_BUCKETS, POPULARITY_BUCKETS + [float('inf')]) if p <= popularity_score < p_next)
    
    # Combine into a single score or prioritize a specific bucket
    # Priority order: Frequency > Density > Popularity
    return f"freq_{f_bucket}density{d_bucket}pop{p_bucket}"

# Iterate over the inverted index
for word_id, doc_data in inverted_idx.items():
    total_freq = sum(doc['freq'] for doc in doc_data.values())  # Total frequency of the word across documents
    for doc_id, metadata in doc_data.items():
        density = metadata['density']
        popularity_score = (
            metadata['stars'] * 0.5 +
            metadata['forks'] * 0.3 +
            metadata['Issues'] * 0.2
        )

        # Determine the most relevant barrel
        barrel_name = assign_to_single_barrel(total_freq, density, popularity_score)

        # Prepare document data
        barrel_data = {
            'word_id': word_id,
            'doc_id': doc_id,
            'frequency': total_freq,
            'density': density,
            'popularity_score': popularity_score,
            'stars': metadata['stars'],
            'forks': metadata['forks'],
            'url': metadata['URL']
        }

        # Append to the appropriate barrel
        barrel_data_dict[barrel_name].append(barrel_data)

# Write all the accumulated barrel data to files at once
for barrel_name, data in barrel_data_dict.items():
    file_path = os.path.join(output_dir, barrel_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

print(f"Barrels have been saved as separate files in the '{output_dir}' directory.")
