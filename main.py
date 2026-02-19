import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 1. API 키 로드
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. prompts.json 로드
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
    # 서버가 API 키를 제대로 읽어왔는지 브라우저에서 바로 확인 가능하도록 추가
    key_status = "Loaded" if GEMINI_API_KEY else "Missing"
    return {"status": "running", "api_key": key_status}

@app.post("/upload")
async def upload_content(request: EssayRequest):
    if not GEMINI_API_KEY:
        print("에러: GEMINI_API_KEY 환경변수가 없습니다.")
        raise HTTPException(status_code=500, detail="서버에 API 키가 설정되지 않았습니다.")

    # 구글 제미나이 REST API 주소 (1.5 Flash 명시)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # REST API 페이로드 규격에 맞게 조립
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
        # [핵심] 라이브러리 없이 직접 통신
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        # HTTP 상태 코드가 200 정상이 아닐 경우, 구글의 '진짜' 에러 메시지를 그대로 반환
        if response.status_code != 200:
            error_msg = response_data.get("error", {}).get("message", "Unknown Google API Error")
            print(f"Google Raw Error: {error_msg}")
            raise HTTPException(status_code=response.status_code, detail=f"구글 API 에러: {error_msg}")
        
        # 정상 응답 파싱
        ai_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return {"result": ai_text}

    except Exception as e:
        print(f"통신 에러 상세: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 에러: {str(e)}")
