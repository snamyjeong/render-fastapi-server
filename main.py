import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# 1. 환경변수 및 제미나이 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 2. prompts.json 로드 (시스템 지침)
def load_system_instruction():
    try:
        with open("prompts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # 성남님이 이전에 정의한 key 이름("system_instructions")을 사용합니다.
            return data.get("system_instructions", "너는 유능한 AI 어시스턴트야.")
    except Exception as e:
        print(f"프롬프트 파일 로드 실패: {e}")
        return "너는 유능한 AI 어시스턴트야."

SYSTEM_INSTRUCTION = load_system_instruction()

class EssayRequest(BaseModel):
    content: str

@app.post("/upload")
async def upload_content(request: EssayRequest):
    try:
        # 3. 모델 설정 (시스템 지침 주입)
        # 제미나이는 모델 생성 시점에 system_instruction을 고정할 수 있습니다.
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 4. 콘텐츠 생성
        response = model.generate_content(request.content)
        
        # 5. 기존 안드로이드 앱과 100% 호환되는 JSON 구조 반환
        return {"result": response.text}

    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
