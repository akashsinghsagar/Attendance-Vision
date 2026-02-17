import pickle

# Sample data structure expected by your app
sample_data = {
    'encodings': [],  # List of face encodings (numpy arrays, empty for now)
    'ids': [],        # List of user IDs
    'names': [],      # List of user names
    'departments': [] # List of user departments
}

with open('encodings.pkl', 'wb') as f:
    pickle.dump(sample_data, f)

print('Sample encodings.pkl created.')
