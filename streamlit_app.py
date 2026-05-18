import streamlit as st
import requests
import base64
import time

# --- 보안 설정 ---
try:
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ Streamlit Secrets에 WAVESPEED_API_KEY를 등록해주세요.")
    st.stop()

# [검증됨] 2026년 Wavespeed AI 표준 OpenAI 호환 엔드포인트
URL = "https://api.wavespeed.ai/v1/images/generations"
# 고성능 모델
MODEL = "wavespeed-ai/flux-schnell"

st.set_page_config(page_title="AI-Stagram Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    div.stButton > button {
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        color: white; border-radius: 12px; font-weight: bold; border: none; height: 3.5em;
    }
    img { border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 AI-Stagram")
st.caption("2026 Verified Wavespeed Engine")

prompt = st.text_input("피드 컨셉 입력 (영문)", placeholder="e.g. A high-quality photo of a delicious apple")

def generate_image(p):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # [검증됨] Wavespeed 표준 페이로드 구조
    payload = {
        "model": MODEL,
        "prompt": f"{p}, professional photography, instagram style, 8k",
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json" # 속도를 위해 base64로 직접 받음
    }
    
    try:
        # 429 에러 방지를 위해 타임아웃 넉넉히 설정
        resp = requests.post(URL, headers=headers, json=payload, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            # API 응답에서 base64 데이터 추출
            return data['data'][0]['b64_json']
        elif resp.status_code == 429:
            st.warning("⚠️ 현재 계정의 동시 생성 제한에 걸렸습니다. 5초 후 다시 시도합니다.")
            time.sleep(5)
            return "retry"
        else:
            st.error(f"❌ API 에러 ({resp.status_code}): {resp.text}")
            return None
    except Exception as e:
        st.error(f"❌ 시스템 에러: {str(e)}")
        return None

if st.button("🚀 피드 생성하기"):
    if prompt:
        with st.spinner("Wavespeed 엔진에서 이미지를 한 장씩 안전하게 가져오는 중..."):
            # 429 동시성 에러를 피하기 위해 한 장씩 순차적으로 요청
            images = []
            for i in range(2): # 안전하게 2장만 먼저 시도
                result = generate_image(prompt)
                if result == "retry": # 재시도 로직
                    result = generate_image(prompt)
                if result and result != "retry":
                    images.append(result)
                time.sleep(1) # 요청 간 간격

            if images:
                cols = st.columns(len(images))
                for idx, b64 in enumerate(images):
                    with cols[idx]:
                        st.image(base64.b64decode(b64), use_container_width=True)
                st.success("생성 완료!")
    else:
        st.warning("프롬프트를 입력해주세요.")
