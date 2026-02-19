import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

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
    return {"status": "running", "model_target": "gemini-2.5-flash"}

@app.post("/upload")
async def upload_content(request: EssayRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="API 키가 없습니다.")

    # [핵심] 성남님 계정에서 지원하는 2.5 Flash 모델 이름으로 정확히 교체
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
            error_msg = response_data.get("error", {}).get("message", "Unknown API Error")
            print(f"Google Raw Error: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=f"API 에러: {error_msg}")
        
        # 응답 파싱
        ai_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return {"result": ai_text}

    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 에러: {str(e)}")
