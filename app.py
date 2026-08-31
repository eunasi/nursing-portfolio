import streamlit as st
import os
from google import genai
import docx
import pypdf

# 화면 설정
st.set_page_config(page_title="간호학과 포트폴리오 점검", layout="centered")
st.title("🩺 간호교육 포트폴리오 AI 점검")
st.write("포트폴리오 파일(PDF/Word)을 업로드하면 AI가 자동 점검합니다.")

# API 키 확인
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에서 GEMINI_API_KEY를 설정해 주세요.")
    st.stop()

client = genai.Client(api_key=api_key)

# 파일 업로드
uploaded_file = st.file_uploader("포트폴리오 파일 선택 (.docx, .pdf)", type=["docx", "pdf"])

def extract_text(file):
    ext = os.path.splitext(file.name)[1].lower()
    full_text = []
    if ext == ".docx":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            full_text.append(para.text)
    elif ext == ".pdf":
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)

if uploaded_file is not None:
    st.info(f"선택된 파일: {uploaded_file.name}")
    if st.button("AI 점검 시작"):
        with st.spinner("AI가 포트폴리오를 분석 중입니다..."):
            try:
                text = extract_text(uploaded_file)
                prompt = f"""
                당신은 간호교육인증평가 전문가입니다.
                다음 포트폴리오 내용을 바탕으로 [1. 강의계획 및 PO-CO 연계성], [2. 학생 평가 도구 및 루브릭], [3. 성과 산출 및 CQI 환류] 항목을 점검해 주세요.
                각 항목별로 [적합], [보완 필요], [미흡] 판정과 함께 구체적인 보완 요구 사항을 작성해 주세요.

                포트폴리오 내용:
                {text}
                """
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                st.success("점검 완료!")
                st.markdown("### 📋 AI 점검 리포트")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")