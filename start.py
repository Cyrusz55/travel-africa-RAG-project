# start.py - launch both servers and upload data if needed
import subprocess, sys, os, time, urllib.request, json

DATA_FLAG = "chroma_db/data_uploaded.flag"

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

    # Upload data only once
    if not os.path.exists(DATA_FLAG):
        print("\nUploading hotel data to vector database...")
        try:
            req = urllib.request.Request("http://localhost:8000/upload-data", method="POST")
            resp = urllib.request.urlopen(req, timeout=120)
            print(resp.read().decode())
            # Create flag so it doesn't run again
            os.makedirs(os.path.dirname(DATA_FLAG), exist_ok=True)
            with open(DATA_FLAG, "w") as f:
                f.write("done")
            print("Done (won't upload again unless flag is deleted).\n")
        except Exception as e:
            print(f"Upload failed: {e}")
    else:
        print("Data already uploaded (flag exists). Skipping upload.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        backend.kill()
        frontend.kill()
        print("Stopped.")
