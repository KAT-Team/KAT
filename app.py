import streamlit as st

st.set_page_config(
    page_title="KAT - KBO 올인원 직관 도우미",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ KAT - KBO 올인원 직관 도우미")
st.caption("KBO 10개 구단의 경기 일정, 예매, 날씨, 교통 정보를 한 곳에서!")

page = st.sidebar.selectbox(
    "메뉴",
    ["경기 일정", "직관 도우미", "구단 순위"]
)

if page == "경기 일정":
    from frontend.pages.schedule import show
    show()
elif page == "직관 도우미":
    from frontend.pages.guide import show
    show()
elif page == "구단 순위":
    from frontend.pages.ranking import show
    show()
