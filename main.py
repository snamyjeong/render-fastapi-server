import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai  # 안정 버전 사용

app = FastAPI()

# 1. 제미나이 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

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
    return {"status": "running", "message": "Gemini Server is Ready"}

@app.post("/upload")
async def upload_content(request: EssayRequest):
    try:
        # [핵심 수정] 모델 이름에서 'models/' 접두사를 빼거나 확실한 모델명을 사용
        # v1beta 에러 방지를 위해 가장 표준적인 생성 방식을 사용합니다.
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 안전한 호출을 위해 명시적으로 contents를 전달
        response = model.generate_content(request.content)
        
        if not response.text:
            raise ValueError("AI가 빈 응답을 반환했습니다.")

        return {"result": response.text}

    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        # 500 에러 시 상세 내용을 로그에 찍어 디버깅을 돕습니다.
        raise HTTPException(status_code=500, detail=f"AI 호출 실패: {str(e)}")
