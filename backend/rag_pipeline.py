import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".secrets"))

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

def ask_question(question: str, api_key: str = None):
    if api_key is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="hotels")
    results = collection.query(query_texts=question, n_results=5)

    context = ""
    sources = []
    for i, doc in enumerate(results['documents'][0]):
        context += f"--Hotel {i + 1} --\n{doc}\n\n"
        sources.append(results['metadatas'][0][i])

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
