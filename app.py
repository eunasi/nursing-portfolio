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
                당신은 간호교육인증평가 및 교육품질관리(CQI) 전문가입니다.
                제출된 문서를 바탕으로 다음 3가지 핵심 항목 및 세부 지표를 엄격히 점검해 주세요.

                [점검 항목 및 세부 평가 기준]

                1. [강의계획 및 PO-CO 연계성]
                   - 교과목 학습성과(CO)와 프로그램 학습성과(PO)의 매핑 및 연계성이 타당한가?
                   - 주차별 수업 내용 및 교수학습방법이 학습성과 달성에 적절한가?

                2. [학생 평가 도구 및 루브릭]
                   - 평가 도구, 채점 기준표(루브릭) 및 성적대별 구비 여부가 적절한가?

                3. [CQI 분석 및 미성취자 환류 관리]
                   - [학습성과별 분석]: 각 학습성과(PO/CO)별 달성도 및 성취 수준에 대한 분석이 면밀하고 구체적으로 이루어졌는가?
                   - [[하] 성취수준 기준 적용 적절성]: 
                     * 대상 학번별 [하] 성취수준 기준이 올바르게 적용되었는지 점검
                     * 2023학번, 2024학번, 2025학번: 달성도 70% 미만이 [하] 성취수준으로 적용되었는가?
                     * 2026학번: 달성도 60% 미만이 [하] 성취수준으로 적용되었는가?
                   - [미성취자 관리 및 환류]: 학습성과 미성취자(해당 학번 기준 [하] 성취수준 학생)에 대한 구체적인 지도, 재평가, 보완 프로그램 등 미성취자 관리가 철저히 수행되었는가?
                   - [차기 학기 환류계획]: 이전 CQI 반영 여부 및 차기 학기 개선계획이 실현 가능하게 작성되었는가?

                [작성 형식]
                - 각 항목별로 [적합], [보완 필요], [미흡] 판정을 명시해 주세요.
                - 대상 학번에 따른 [하] 성취수준 절단값(70% 미만 / 60% 미만) 오적용이나, 미성취자에 대한 관리 방안 미비 시 구체적인 보완 요구사항을 명확히 지적해 주세요.

                제출 문서 내용:
                {text}
                """
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                st.success("점검 완료!")
                st.markdown("### 📋 AI 점검 리포트")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
