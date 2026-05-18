import streamlit as st
import httpx
import asyncio
import base64

# --- 보안: Streamlit Secrets에서 API 키 로드 ---
try:
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ [설정 필요] Streamlit Cloud 설정에서 'WAVESPEED_API_KEY'를 추가해주세요.")
    st.stop()

URL = "https://api.wavespeed.ai/v1/images/generations"
MODEL = "wavespeed-ai/flux-schnell"

st.set_page_config(page_title="AI-Stagram Pro", layout="wide")

# 인스타그램 느낌의 스타일 시트
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div.stButton > button {
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        color: white; border-radius: 12px; font-weight: bold; border: none; width: 100%;
    }
    img { border-radius: 12px; transition: transform 0.3s; }
    img:hover { transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 AI-Stagram")
st.caption("2026 WaveSpeed Flux-Schnell Engine | Ultra Fast Mode")

# 입력창
prompt = st.text_input("피드 컨셉을 입력하세요 (영문 권장)", placeholder="e.g. A trendy Seoul cafe with neon signs")

async def generate_single_image(client, prompt):
    """WaveSpeed API 호출 함수"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "prompt": f"{prompt}, professional photography, instagram aesthetic, high quality, 8k",
        "size": "1024x1024",
        "response_format": "b64_json"
    }
    try:
        resp = await client.post(URL, headers=headers, json=payload, timeout=60.0)
        if resp.status_code == 200:
            return resp.json()['data'][0]['b64_json']
        return None
    except:
        return None

async def run_parallel_generation(prompt):
    """6개 이미지를 병렬로 동시 생성"""
    async with httpx.AsyncClient() as client:
        tasks = [generate_single_image(client, prompt) for _ in range(6)]
        return await asyncio.gather(*tasks)

if st.button("🚀 새로운 피드 생성"):
    if prompt:
        with st.spinner("AI가 고화질 이미지를 생성 중입니다..."):
            # 병렬 실행
            results = asyncio.run(run_parallel_generation(prompt))
            images = [r for r in results if r]

            if images:
                # 3열 인스타 그리드 배치
                cols = st.columns(3)
                for idx, b64_data in enumerate(images):
                    with cols[idx % 3]:
                        st.image(base64.b64decode(b64_data), use_container_width=True)
                st.success(f"총 {len(images)}개의 게시물을 생성했습니다!")
            else:
                st.error("이미지 생성에 실패했습니다. API 키의 유효성이나 할당량을 확인하세요.")
    else:
        st.warning("프롬프트를 입력해주세요.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>© 2026 AI-Stagram Enterprise Edition</p>", unsafe_allow_html=True)
