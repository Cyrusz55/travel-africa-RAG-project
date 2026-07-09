# run.py - launch both servers and upload data only if ChromaDB is empty
import subprocess, sys, os, time, urllib.request, json

CHROMA_DB_PATH = "chroma_db"

def is_data_uploaded():
    """Check if the hotels collection exists in ChromaDB."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(name="hotels")
        return collection.count() > 0
    except Exception:
        return False

if __name__ == "__main__":
    print("Starting Travel Africa RAG...")

    # Start backend
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"]
    )

    # Start frontend server
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5500"]
    )

    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:5500/templates/")

    # Wait for backend to be ready
    for i in range(30):
        try:
            urllib.request.urlopen("http://localhost:8000/", timeout=2)
            break
        except Exception:
            time.sleep(1)

    # Upload data only if not already in ChromaDB
    if is_data_uploaded():
        print("Data already in ChromaDB. Skipping upload.\n")
    else:
        print("\nUploading hotel data to vector database...")
        try:
            req = urllib.request.Request("http://localhost:8000/upload-data", method="POST")
            resp = urllib.request.urlopen(req, timeout=600)
            print(resp.read().decode())
        except Exception as e:
            print(f"Upload timed out but might have completed. Check server output above.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend.kill()
        frontend.kill()
        print("Stopped.")
