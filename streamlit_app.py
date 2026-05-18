import streamlit as st
import requests
import base64
import time

# --- 보안 설정 ---
try:
    API_KEY = st.secrets["WAVESPEED_API_KEY"]
except:
    st.error("⚠️ Streamlit Secrets에 API 키를 등록해주세요.")
    st.stop()

# 엔드포인트 주소
URL = "https://api.siliconflow.cn/v1/images/generations"

# [수정] 만약 Flux가 계속 막힌다면 아래 모델명 중 하나로 바꿔보세요.
# 1순위: black-forest-labs/FLUX.1-schnell
# 2순위: stabilityai/stable-diffusion-3-medium
MODEL = "black-forest-labs/FLUX.1-schnell"

st.set_page_config(page_title="AI-Stagram Pro", layout="wide")

st.title("📸 AI-Stagram")
st.caption(f"Model: {MODEL} | Sequential Mode")

prompt = st.text_input("피드 컨셉 입력 (영문)", placeholder="e.g. A shiny red apple on a white table")

def generate_image(p):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "prompt": f"{p}, high quality, instagram style",
        "image_size": "1024x1024",
        "batch_size": 1,
        "num_inference_steps": 4
    }
    
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=60)
        
        if resp.status_code == 200:
            data = resp.json()
            img_url = data['images'][0]['url']
            return img_url
        elif resp.status_code == 429:
            st.warning("⚠️ 서버의 동시 접속 제한에 걸렸습니다. 잠시 후 자동으로 재시도합니다.")
            time.sleep(5) # 5초 대기 후 재시도 로직
            return "retry"
        else:
            st.error(f"❌ 에러 발생 ({resp.status_code}): {resp.text}")
            return None
    except Exception as e:
        st.error(f"❌ 시스템 에러: {str(e)}")
        return None

if st.button("🚀 피드 생성하기"):
    if prompt:
        with st.spinner("서버 상태를 확인하며 한 장씩 생성 중입니다..."):
            images = []
            # 동시 접속 제한을 피하기 위해 한 장씩 순차적으로 생성
            for i in range(2): # 일단 안전하게 2장만 시도
                result = generate_image(prompt)
                
                if result == "retry": # 재시도 로직
                    result = generate_image(prompt)
                
                if result and result != "retry":
                    images.append(result)
                    time.sleep(2) # 생성 간격 사이에 2초 휴식 (매우 중요)

            if images:
                cols = st.columns(len(images))
                for idx, url in enumerate(images):
                    with cols[idx]:
                        st.image(url, use_container_width=True)
                st.success("생성 완료!")
            else:
                st.info("💡 만약 계속 429 에러가 난다면, SiliconCloud 설정에서 휴대폰 인증을 완료하거나 최소 금액($1)을 충전해야 할 수 있습니다.")
    else:
        st.warning("프롬프트를 입력해주세요.")
