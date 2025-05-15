import pickle

with open("./output_faiss2/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Metadata count:", len(metadata))
print("Sample:", metadata[0])
