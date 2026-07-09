# Build vector database with ONNX embedding (no torch needed)
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
import pandas as pd
import os

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

def create_embeddings():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    df = pd.read_csv(os.path.join(data_dir, "clean_data/cleaned_hotels.csv"))

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # ONNX-based all-MiniLM-L6-v2 (lightweight, no torch/sentence-transformers)
    emb_fn = ONNXMiniLM_L6_V2()
    collection = client.get_or_create_collection(
        name="hotels", embedding_function=emb_fn
    )

    for _, row in df.iterrows():
        doc_text = f"""
        Hotel Name: {row['Hotel Name']}
Location: {row['Location']}, {row['County or Region']}, {row['Country']}
Description: {row['Hotel Description']}
Amenities: {row['Amenities']}
Contact Information: {row['Contact Information']}
""".strip()

        collection.add(
            documents=[doc_text],
            metadatas=[{
                "hotel_name": row['Hotel Name'],
                "location": row['Location'],
                "price_range": row['Price Range'],
                "source_url": row['Website URL'],
            }],
            ids=[f"{row['Hotel Name']}_{row['Location']}"]
        )

    print(f"Stored {len(df)} hotel embeddings in the ChromaDB vector database.")
    return collection
