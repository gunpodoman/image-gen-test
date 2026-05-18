import streamlit as st
import requests
import base64

# --- 보안 설정 ---
try:
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ Streamlit Secrets에 API 키를 등록해주세요.")
    st.stop()

# 2026년 5월 기준 가장 안정적인 SiliconCloud/WaveSpeed 통합 주소
URL = "https://api.siliconflow.cn/v1/images/generations"
# 고성능 Flux-Schnell 모델
MODEL = "black-forest-labs/FLUX.1-schnell"

st.set_page_config(page_title="AI-Stagram PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div.stButton > button {
        background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        color: white; border-radius: 12px; font-weight: bold; border: none; height: 3.5em;
    }
    img { border-radius: 12px; transition: 0.3s; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 AI-Stagram")
st.caption("2026 Flux Engine | High Performance Mode")

prompt = st.text_input("피드 컨셉 입력 (영문)", placeholder="e.g. A futuristic luxury cafe, cinematic lighting, 8k")

def generate_image(p):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # 2026년 표준 규격 페이로드
    payload = {
        "model": MODEL,
        "prompt": f"{p}, professional photography, instagram aesthetic, high quality, 8k",
        "image_size": "1024x1024",
        "batch_size": 1,
        "num_inference_steps": 4
    }
    
    try:
        # verify=True가 기본이지만 에러 발생 시를 대비해 로직 보강
        resp = requests.post(URL, headers=headers, json=payload, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            # 2026년 API는 이미지를 URL 형태로 주는 경우가 많습니다.
            img_url = data['images'][0]['url']
            img_content = requests.get(img_url).content
            return base64.b64encode(img_content).decode('utf-8')
        else:
            st.error(f"❌ API 에러: {resp.status_code}\n내용: {resp.text}")
            return None
    except Exception as e:
        st.error(f"❌ 시스템 에러: {str(e)}")
        return None

if st.button("🚀 새로운 피드 생성하기"):
    if prompt:
        with st.spinner("AI가 고화질 피드를 생성 중입니다..."):
            # 안정적인 생성을 위해 3장을 순차적으로 생성
            images = []
            for i in range(3):
                img_data = generate_image(prompt)
                if img_data:
                    images.append(img_data)
            
            if images:
                cols = st.columns(3)
                for idx, b64 in enumerate(images):
                    with cols[idx]:
                        st.image(base64.b64decode(b64), use_container_width=True)
                st.success("피드 생성 완료!")
    else:
        st.warning("프롬프트를 입력해주세요.")
