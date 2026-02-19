# main.py 예시
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class EssayRequest(BaseModel):
    content: str  # 안드로이드의 EssayRequest(val content: String)과 매칭

@app.get("/")
def read_root():
    return "OK"

@app.post("/upload") # 👈 안드로이드 ApiService의 @POST("upload")와 매칭
async def upload_essay(request: EssayRequest):
    print(f"받은 내용: {request.content}") 
    
    # 💡 여기서 OpenAI API를 호출하여 분석 결과를 가져옵니다.
    # 일단 테스트를 위해 받은 내용을 그대로 반환해 보겠습니다.
    return {"result": f"서버가 정상적으로 수신함: {request.content[:30]}..."}
