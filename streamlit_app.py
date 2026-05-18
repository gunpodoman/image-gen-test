import streamlit as st
import httpx
import asyncio
import base64

# --- 설정 (제공해주신 WaveSpeed API 키 적용) ---
API_KEY = "b87adbd21652130ce5342befac412714ed3bf543a5d7360fbd2eab936afdb8a7"
URL = "https://api.wavespeed.ai/v1/images/generations"
MODEL = "wavespeed-ai/flux-schnell"

st.set_page_config(page_title="AI-Stagram Pro", layout="wide")

# --- 인스타그램 스타일 CSS ---
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color: white; border: none; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 20px; }
    img { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 AI-Stagram PRO")
st.caption("Powered by WaveSpeed AI - 2026 High-Speed Engine")

# --- 사이드바 및 입력 ---
with st.sidebar:
    st.header("Profile")
    st.info("🎨 WaveSpeed_AI_Artist\n\nFollowers: 2.6M")
    prompt = st.text_input("어떤 피드를 만들까요? (영어로 입력)", placeholder="e.g. A futuristic city cafe")

# --- 이미지 생성 함수 ---
async def generate_image(client, prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "prompt": f"{prompt}, instagram aesthetic, high quality, 8k",
        "size": "1024x1024",
        "response_format": "b64_json"
    }
    try:
        resp = await client.post(URL, headers=headers, json=payload, timeout=60.0)
        if resp.status_code == 200:
            return resp.json()['data'][0]['b64_json']
    except:
        return None
    return None

async def run_batch(prompt):
    async with httpx.AsyncClient() as client:
        tasks = [generate_image(client, prompt) for _ in range(6)]
        return await asyncio.gather(*tasks)

# --- 메인 화면 로직 ---
if st.button("피드 생성하기"):
    if prompt:
        with st.spinner("AI가 고화질 피드를 찍어내고 있습니다..."):
            # 6개 병렬 생성
            results = asyncio.run(run_batch(prompt))
            images = [r for r in results if r is not None]

            if images:
                # 인스타그램 3열 그리드 재현
                cols = st.columns(3)
                for idx, b64_str in enumerate(images):
                    with cols[idx % 3]:
                        st.image(base64.b64decode(b64_str), use_container_width=True)
            else:
                st.error("생성에 실패했습니다. API 키나 서버 상태를 확인하세요.")
    else:
        st.warning("프롬프트를 입력해주세요!")

# --- 하단 히스토리 안내 ---
st.divider()
st.center = st.markdown("<p style='text-align: center; color: gray;'>© 2026 AI-Stagram with WaveSpeed AI</p>", unsafe_allow_html=True)
