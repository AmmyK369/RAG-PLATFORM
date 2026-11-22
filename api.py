import json, os, secrets, uuid
from datetime import datetime
from fastapi import FastAPI, Depends, Header, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

import rag
from uploader import ingest_file

app = FastAPI(title="Amara Tech Knowledge Assistant")
VALID_ROLES = {"employee", "engineer", "admin"}


USERS = {
    "emma":  {"password": "emma123",  "role": "employee"},
    "ethan": {"password": "ethan123", "role": "engineer"},
    "alice": {"password": "alice123", "role": "admin"},
}
TOKENS = {}     
MESSAGES = {}   

class LoginRequest(BaseModel):
    username: str
    password: str

class AskRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    message_id: str
    rating: str   # "up" or "down"
    
def current_user(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    user = TOKENS.get(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in first")
    return user

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "chunks_loaded": len(rag.ALL_CHUNKS)}

@app.post("/login")
def login(body: LoginRequest):
    name = body.username.lower()
    user = USERS.get(name)
    if user is None or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    token = secrets.token_hex(16)
    TOKENS[token] = {"username": name, "role": user["role"]}
    return {"token": token, "username": name, "role": user["role"]}

@app.post("/ask")
def ask(body: AskRequest, user=Depends(current_user)):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty")
    result = rag.answer(question, role=user["role"])
    message_id = uuid.uuid4().hex[:8]
    MESSAGES[message_id] = {"question": question, "answer": result["answer"], "role": user["role"]}
    return {"message_id": message_id, "answer": result["answer"], "sources": result["sources"]}

@app.post("/feedback")
def feedback(body: FeedbackRequest, user=Depends(current_user)):
    if body.rating not in ("up", "down"):
        raise HTTPException(status_code=400, detail="rating must be 'up' or 'down'")
    msg = MESSAGES.get(body.message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="Unknown message")
    record = {**msg, "rating": body.rating, "user": user["username"],
              "time": datetime.now().isoformat()}
    with open("feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"saved": True}

@app.post("/admin/upload")
def upload(file: UploadFile = File(...), roles: str = Form(...), user=Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    chosen = [r.strip() for r in roles.split(",") if r.strip()]
    if not chosen or not set(chosen) <= VALID_ROLES:
        raise HTTPException(status_code=400, detail="Choose at least one valid role")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".txt", ".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only .txt, .pdf and .docx are supported")
    os.makedirs("data/uploads", exist_ok=True)
    path = os.path.join("data/uploads", os.path.basename(file.filename))
    with open(path, "wb") as f:
        f.write(file.file.read())
    count = ingest_file(path, chosen)
    return {"file": file.filename, "chunks_added": count, "roles": chosen}