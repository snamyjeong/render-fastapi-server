from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

# 기존 루트가 있다면 유지
@app.get("/", response_class=PlainTextResponse)
def root():
    return "OK"

# 헬스체크(모니터링/배포 확인용)
@app.get("/health", response_class=PlainTextResponse)
def health():
    return "healthy"