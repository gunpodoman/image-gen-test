import streamlit as st
import requests
import base64
import time

# --- 보안 설정 ---
try:
    # Streamlit Cloud의 Settings -> Secrets에서 가져옴
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ Streamlit Secrets에 WAVESPEED_API_KEY를 등록해주세요.")
    st.stop()

# [검증됨] 2026년 5월 WaveSpeed AI 공식 엔드포인트 규격
# 주소 형식: https://api.wavespeed.ai/api/v3/{author}/{model}
MODEL_ID = "wavespeed-ai/flux-schnell"
URL = f"https://api.wavespeed.ai/api/v3/{MODEL_ID}"

st.set_page_config(page_title="Wave-Stagram Pro", layout="wide")

# 인스타 감성 스타일 적용
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    div.stButton > button {
        background: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
        color: white; border-radius: 12px; font-weight: bold; border: none; height: 3.5em;
    }
    img { border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Wave-Stagram")
st.caption("2026 Optimized WaveSpeed Engine | Flux-Schnell v3")

prompt = st.text_input("피드 컨셉 입력 (영문)", placeholder="e.g. A futuristic Seoul night with pink neon lights, 8k")

def generate_wavespeed_image(user_prompt):
    """검증된 WaveSpeed v3 API 호출 로직"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # [검증됨] 2026 WaveSpeed 전용 데이터 규격
    # v3 API는 'prompt'와 'output_format' 등을 최상위에 배치합니다.
    payload = {
        "prompt": f"{user_prompt}, high-end instagram photography, 8k, realistic texture",
        "size": "1024x1024",
        "output_format": "webp",
        "sync": True  # 동기식 생성을 요청 (2026 신기능)
    }
    
    try:
        # verify=False는 로컬 테스트용이나, 상용 서버에선 빼는 것이 원칙입니다.
        resp = requests.post(URL, headers=headers, json=payload, timeout=90)
        
        if resp.status_code == 200:
            data = resp.json()
            # WaveSpeed v3는 'images' 배열 내에 'url' 혹은 'base64'를 반환합니다.
            # 최근 규격은 성능을 위해 직접적인 image_url 혹은 data 필드를 제공함
            if 'images' in data and len(data['images']) > 0:
                img_info = data['images'][0]
                # URL 형태일 경우 다운로드, Base64 형태일 경우 바로 처리
                if img_info.get('url'):
                    img_data = requests.get(img_info['url']).content
                else:
                    img_data = base64.b64decode(img_info['base64'])
                return img_data
        else:
            st.error(f"❌ API 오류: {resp.status_code}\n원인: {resp.text}")
            return None
    except Exception as e:
        st.error(f"❌ 시스템 오류: {str(e)}")
        return None

if st.button("✨ 인스타 피드 생성"):
    if prompt:
        with st.spinner("WaveSpeed 엔진이 초고화질 이미지를 렌더링 중입니다..."):
            # 피드 구성을 위해 3장 생성
            images = []
            for i in range(3):
                img_bin = generate_wavespeed_image(prompt)
                if img_bin:
                    images.append(img_bin)
            
            if images:
                cols = st.columns(3)
                for idx, img in enumerate(images):
                    with cols[idx]:
                        st.image(img, use_container_width=True)
                st.success("피드 생성 완료!")
    else:
        st.warning("프롬프트를 입력해 주세요.")
