import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()

# [보안] 환경 변수에서 API 키 로드
API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=API_KEY)

class EssayRequest(BaseModel):
    content: str

# [Helper] JSON에서 프롬프트 읽기 함수
def get_prompt_from_json():
    try:
        # 파일 경로를 절대 경로로 잡는 것이 안전합니다 (Render/WSL 공통)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "prompts.json")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("system_instructions", "")
    except Exception as e:
        print(f"JSON 로드 에러: {e}")
        # 파일이 없을 때를 대비한 최소한의 Fallback 프롬프트
        return "너는 엔지니어의 비서 JAVIS야. 입력에 대해 정중히 응답해줘."

@app.get("/")
def read_root():
    return "OK"

@app.post("/upload")
async def handle_essay(request: EssayRequest):
    user_text = request.content
    
    if not API_KEY:
        return {"result": "서버 설정 에러: API 키가 없습니다."}

    # API 호출 시마다 JSON을 다시 읽어오므로, 파일 수정 후 재배포 없이(또는 재시작 후) 즉시 반영됩니다.
    system_prompt = get_prompt_from_json()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        
        ai_result = response.choices[0].message.content
        return {"result": ai_result}

    except Exception as e:
        return {"result": f"AI 분석 중 오류 발생: {str(e)}"}
