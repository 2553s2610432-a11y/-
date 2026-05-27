import streamlit as st
import google.generativeai as genai

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="일정 정리 챗봇",
    page_icon="📅",
    layout="centered"
)

# -----------------------------
# API KEY 설정
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

except Exception:
    st.error("API KEY를 불러오지 못했습니다.")
    st.stop()

# -----------------------------
# Gemini 모델 설정
# -----------------------------
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction="""
        너는 일정 정리 전문 AI 비서다.

        사용자의 일정을:
        - 시간 순서대로 정리하고
        - 보기 쉽게 요약하며
        - 중요 일정은 강조하고
        - 일정 충돌이 있으면 알려준다.

        항상 한국어로 답변한다.
        """
    )

except Exception as e:
    st.error(f"모델 초기화 오류: {e}")
    st.stop()

# -----------------------------
# 제목
# -----------------------------
st.title("📅 일정 정리 Gemini 챗봇")

st.caption("일정을 입력하면 깔끔하게 정리해드립니다.")

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 이전 채팅 출력
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
prompt = st.chat_input("일정을 입력하세요")

# -----------------------------
# 입력 처리
# -----------------------------
if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini 응답
    with st.chat_message("assistant"):

        message_placeholder = st.empty()
        full_response = ""

        try:
            # 대화 기록 구성
            history_text = ""

            for msg in st.session_state.messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                history_text += f"{role}: {msg['content']}\n"

            # 프롬프트 생성
            final_prompt = f"""
            아래는 사용자와의 이전 대화 내용이다.

            {history_text}

            마지막 사용자 요청에 맞게
            일정을 체계적으로 정리해줘.
            """

            # 스트리밍 응답
            response = model.generate_content(
                final_prompt,
                stream=True
            )

            for chunk in response:

                if hasattr(chunk, "text") and chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:

            error_message = f"""
            ⚠️ 오류가 발생했습니다.

            오류 내용:
            {str(e)}
            """

            message_placeholder.error(error_message)
            full_response = error_message

    # 응답 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )
