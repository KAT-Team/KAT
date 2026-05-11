"""
경기 일정 캘린더 페이지
- KBO 전 구단 경기 일정 통합 조회
- 구단별 필터링
- 예매 링크 바로가기
"""

import streamlit as st
from backend.data.collect import TEAMS, get_ticket_link


def show():
    st.header("📅 경기 일정")
    st.write("KBO 10개 구단의 경기 일정을 한눈에 확인하세요!")

    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox(
            "구단 선택",
            ["전체"] + list(TEAMS.keys()),
            format_func=lambda x: "전체 구단" if x == "전체" else str(TEAMS.get(x, x))
        )
    with col2:
        selected_month = st.selectbox(
            "월 선택",
            list(range(3, 11)),
            index=2,
            format_func=lambda x: f"{x}월"
        )

    # TODO: 실제 경기 일정 데이터 연동 필요
    st.info("경기 일정 데이터를 불러오는 중입니다...")

    # TODO: calendar_view.py 연동 필요

    if selected_team != "전체":
        ticket_url = get_ticket_link(selected_team)
        st.markdown(f"### 🎟️ [{TEAMS[selected_team]} 티켓 예매 바로가기]({ticket_url})")
