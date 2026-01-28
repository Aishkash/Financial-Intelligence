from fastapi import FastAPI

app = FastAPI(title="AI Transaction Risk System")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Risk system running"}