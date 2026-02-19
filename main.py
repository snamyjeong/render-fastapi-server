import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai  # 최신 라이브러리로 변경

app = FastAPI()

# 1. 제미나이 설정 (최신 SDK 방식)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. prompts.json 로드
def load_system_instruction():
    try:
        with open("prompts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("system_instructions", "너는 유능한 AI 비평가야.")
    except Exception as e:
        return "너는 유능한 AI 비평가야."

SYSTEM_INSTRUCTION = load_system_instruction()

class EssayRequest(BaseModel):
    content: str

# [추가] 브라우저 접속 시 404 방지용 (상태 체크)
@app.get("/")
async def root():
    return {"status": "running", "message": "Gemini AI Server is Live"}

# [핵심] 안드로이드와 통신하는 경로
@app.post("/upload")
async def upload_content(request: EssayRequest):
    try:
        # 최신 SDK의 호출 방식
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=request.content,
            config={
                "system_instruction": SYSTEM_INSTRUCTION
            }
        )
        
        return {"result": response.text}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
