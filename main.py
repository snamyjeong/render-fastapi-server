import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# 1. API 키 설정 및 디버깅 로그
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("CRITICAL: GEMINI_API_KEY가 설정되지 않았습니다!")
else:
    print(f"INFO: API KEY 로드 성공 (앞 4자리: {GEMINI_API_KEY[:4]}...)")

genai.configure(api_key=GEMINI_API_KEY)

# 2. 사용 가능한 모델 리스트 출력 (서버 시작 시 로그 확인용)
try:
    print("--- 사용 가능한 모델 리스트 ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
    print("------------------------------")
except Exception as e:
    print(f"모델 리스트 확인 실패: {e}")

# 3. prompts.json 로드
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
    return {"status": "running", "instruction": SYSTEM_INSTRUCTION[:20] + "..."}

@app.post("/upload")
async def upload_content(request: EssayRequest):
    try:
        # 모델 명칭에서 'models/'를 빼고 'gemini-1.5-flash'만 입력해 봅니다.
        # SDK 버전이 높으면 알아서 처리합니다.
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(request.content)
        
        return {"result": response.text}

    except Exception as e:
        # 에러 발생 시 로그에 상세 출력
        error_msg = str(e)
        print(f"Gemini Error Details: {error_msg}")
        
        # 만약 1.5 Flash가 계속 실패하면 구형 모델로 폴백(Fallback) 시도
        if "404" in error_msg:
            try:
                print("1.5-flash 실패, gemini-pro로 재시도합니다.")
                fallback_model = genai.GenerativeModel('gemini-pro')
                response = fallback_model.generate_content(request.content)
                return {"result": response.text + "\n(Note: gemini-pro fallback)"}
            except Exception as fe:
                raise HTTPException(status_code=500, detail=f"All models failed: {str(fe)}")
        
        raise HTTPException(status_code=500, detail=f"AI 호출 실패: {error_msg}")
