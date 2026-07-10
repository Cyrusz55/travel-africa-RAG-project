# Build vector database with ONNX embedding (no torch needed)
from sqlalchemy import text
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from database.db_connection import get_engine
import pandas as pd
import psycopg2

emb_fn = ONNXMiniLM_L6_V2()

# Build vector_str inline to avoid f-string escaping issues
def _vec_to_str(vector):
    return "[" + ",".join(str(x) for x in vector) + "]"


def create_embeddings():
    df = pd.read_csv("data/clean_data/cleaned_hotels.csv")
    engine = get_engine()

    # Truncate via SQLAlchemy
    with engine.connect() as conn:
        conn.execute(text("truncate table hotels restart identity cascade"))
        conn.commit()

    # Get raw psycopg2 connection for vector casting
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            for _, row in df.iterrows():
                doc_text = f"""Hotel Name: {row['Hotel Name']}
Location: {row['Location']}, {row['County or Region']}, {row['Country']}
Description: {row['Hotel Description']}
Amenities: {row['Amenities']}
Contact Information: {row['Contact Information']}""".strip()

                vector = emb_fn([doc_text])[0]
                vector_str = _vec_to_str(vector)

                cur.execute(
                    """
                    insert into hotels (name, location, county_region, country,
                        description, price_range, amenities, category, contact, website, embedding)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                    """,
                    (
                        row["Hotel Name"],
                        row["Location"],
                        row["County or Region"],
                        row["Country"],
                        row["Hotel Description"],
                        row["Price Range"],
                        row["Amenities"],
                        row["Hotel Category"],
                        row["Contact Information"],
                        row["Website URL"],
                        vector_str,
                    ),
                )
        raw_conn.commit()
    finally:
        raw_conn.close()

    print(f"Stored {len(df)} hotel embeddings in Supabase pgvector.")
