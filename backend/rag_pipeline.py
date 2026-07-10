import os
from openai import OpenAI
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from database.db_connection import get_engine

load_dotenv(".secrets")

emb_fn = ONNXMiniLM_L6_V2()


def _vec_to_str(vector):
    return "[" + ",".join(str(x) for x in vector) + "]"


def ask_question(question: str, api_key: str = None):
    if api_key is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")

    query_vector = emb_fn([question])[0]
    vector_str = _vec_to_str(query_vector)

    engine = get_engine()
    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cur:
            cur.execute(
                """
                select name, location, description, price_range, website,
                       1 - (embedding <=> %s::vector) as similarity
                from hotels
                order by embedding <=> %s::vector
                limit 5
                """,
                (vector_str, vector_str),
            )
            rows = cur.fetchall()
    finally:
        raw_conn.close()

    context = ""
    sources = []
    for i, row in enumerate(rows):
        name, location, description, price_range, website = row[0], row[1], row[2], row[3], row[4]
        context += f"--Hotel {i + 1} --\nName: {name}\nLocation: {location}\nDescription: {description}\n\n"
        sources.append({"hotel_name": name, "location": location})

    if api_key:
        client_llm = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client_llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": "You are a travel assistant for Kenya & East Africa. Use ONLY the provided hotel data. Always mention specific hotel names."},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"}
            ]
        )
        answer = response.choices[0].message.content
    else:
        answer = f"Found {len(sources)} relevant hotels:\n\n"
        for s in sources:
            answer += f"- {s['hotel_name']} in {s['location']}\n"
        answer += "\nPlease provide a DeepSeek API key to get a detailed answer."

    return {"answer": answer, "sources": sources}
