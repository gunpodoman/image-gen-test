import os
import uuid
import base64
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 이미지 저장 경로
IMAGE_DIR = "static/feeds"
os.makedirs(IMAGE_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# WaveSpeed AI 설정
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY", "b87adbd21652130ce5342befac412714ed3bf543a5d7360fbd2eab936afdb8a7")
WAVESPEED_URL = "https://api.wavespeed.ai/v1/images/generations"
# 2026년 가장 빠르고 정확한 모델
MODEL_NAME = "wavespeed-ai/flux-schnell"

class GenerateRequest(BaseModel):
    prompt: str

async def call_wavespeed_api(client, prompt, index):
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    # 인스타 감성 강제 주입 프롬프트
    enhanced_prompt = f"{prompt}, high-end instagram photography, aesthetic lighting, 8k, shot on iPhone 17 Pro"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": enhanced_prompt,
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json" # 2026년 표준: 즉각적인 base64 반환
    }

    try:
        resp = await client.post(WAVESPEED_URL, headers=headers, json=payload, timeout=60.0)
        if resp.status_code == 200:
            data = resp.json()
            b64_data = data['data'][0]['b64_json']
            img_bytes = base64.b64decode(b64_data)
            
            # 로컬 저장 (영구 보관용)
            filename = f"ws_{uuid.uuid4().hex[:10]}.jpg"
            filepath = os.path.join(IMAGE_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            
            print(f"✅ WaveSpeed 생성 성공: {index+1}/6")
            return f"data:image/jpeg;base64,{b64_data}"
        else:
            print(f"❌ API 에러: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"❗ 예외 발생: {e}")
        return None

@app.post("/generate")
async def generate(request: GenerateRequest):
    print(f"🚀 WaveSpeed 엔진 가동 중: {request.prompt}")
    async with httpx.AsyncClient(verify=False) as client:
        # WaveSpeed는 고병렬을 지원하므로 6개를 한꺼번에 생성
        tasks = [call_wavespeed_api(client, request.prompt, i) for i in range(6)]
        results = await asyncio.gather(*tasks)
        images = [img for img in results if img]
        
        if not images:
            raise HTTPException(status_code=500, detail="WaveSpeed API 호출 실패")
        return {"images": images}

@app.get("/images")
async def get_history():
    files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith('.jpg')], 
                   key=lambda x: os.path.getmtime(os.path.join(IMAGE_DIR, x)), reverse=True)
    return {"images": [f"/static/feeds/{f}" for f in files]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
