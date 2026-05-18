import streamlit as st
import requests
import base64
import time

# --- 보안: Streamlit Secrets에서 API 키 로드 ---
try:
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ [설정 필요] Streamlit Cloud Settings -> Secrets에 WAVESPEED_API_KEY를 추가하세요.")
    st.stop()

# WaveSpeed AI 설정 (2026 규격)
URL = "https://api.wavespeed.ai/v1/images/generations"
MODEL = "wavespeed-ai/flux-schnell"

st.set_page_config(page_title="AI-Stagram Pro", layout="wide")

# UI 디자인
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div.stButton > button {
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        color: white; border-radius: 12px; font-weight: bold; border: none; width: 100%; height: 3em;
    }
    .stTextInput>div>div>input { border-radius: 10px; }
    img { border-radius: 12px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 AI-Stagram")
st.caption("2026 WaveSpeed Flux-Schnell | Stable Engine")

# 입력창
prompt = st.text_input("피드 컨셉 입력 (영문)", placeholder="e.g. Delicious apple on a wooden table, 8k")

def generate_image(p):
    """동기 방식(requests)으로 변경하여 안정성 확보"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "prompt": f"{p}, professional photography, instagram aesthetic, high quality",
        "size": "1024x1024",
        "n": 1,
        "response_format": "b64_json",  # Base64 출력을 명시
        "enable_base64_output": True    # WaveSpeed 전용 파라미터 추가
    }
    
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            # 응답 구조 확인 후 데이터 추출
            data = resp.json()
            return data['data'][0]['b64_json']
        else:
            # 에러 발생 시 화면에 상세 코드 출력
            st.error(f"❌ API 에러: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        st.error(f"❌ 연결 에러: {str(e)}")
        return None

if st.button("🚀 새로운 피드 생성"):
    if prompt:
        with st.spinner("AI가 작업 중입니다..."):
            # 아이패드 브라우저 안정성을 위해 3장만 먼저 테스트
            images = []
            for i in range(3):
                img_data = generate_image(prompt)
                if img_data:
                    images.append(img_data)
                time.sleep(0.5) # 과부하 방지

            if images:
                cols = st.columns(3)
                for idx, b64_str in enumerate(images):
                    with cols[idx]:
                        st.image(base64.b64decode(b64_str), use_container_width=True)
                st.success(f"{len(images)}개의 게시물 생성 완료!")
    else:
        st.warning("프롬프트를 입력하세요.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>© 2026 AI-Stagram PRO</p>", unsafe_allow_html=True)
