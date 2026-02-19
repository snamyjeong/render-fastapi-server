import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. API 키 로드
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def load_system_instruction():
    try:
        if os.path.exists("prompts.json"):
            with open("prompts.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("system_instructions", "너는 유능한 AI 비평가야.")
        return "너는 유능한 AI 비평가야."
    except Exception:
        return "너는 유능한 AI 비평가야."

SYSTEM_INSTRUCTION = load_system_instruction()

class EssayRequest(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"status": "running", "api_key_loaded": bool(GEMINI_API_KEY)}

# [추가] 내 API 키로 쓸 수 있는 모델이 뭔지 구글에 직접 물어보는 주소
@app.get("/models")
async def check_available_models():
    if not GEMINI_API_KEY:
        return {"error": "API Key is missing"}
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    response = requests.get(url)
    return response.json()

@app.post("/upload")
async def upload_content(request: EssayRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="서버에 API 키가 설정되지 않았습니다.")

    # 1.5-flash-latest 로 이름 살짝 변경 (혹시 모를 별칭 문제 대비)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [
            {"parts": [{"text": request.content}]}
        ]
    }
    
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            error_msg = response_data.get("error", {}).get("message", "Unknown Google API Error")
            print(f"Google Raw Error: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=f"구글 API 에러: {error_msg}")
        
        ai_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return {"result": ai_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"내부 에러: {str(e)}")
