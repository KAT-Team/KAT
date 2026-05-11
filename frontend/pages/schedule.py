"""
경기 일정 캘린더 페이지
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from backend.data.collect import TEAMS, get_schedule, get_ticket_link
from backend.data.preprocess import preprocess_schedule, filter_by_team
from frontend.components.calendar_view import draw_schedule_table, draw_monthly_chart


def show():
    st.header("📅 경기 일정")
    st.write("KBO 10개 구단의 경기 일정을 한눈에 확인하세요!")

    # 필터
    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox(
            "구단 선택",
            ["전체"] + list(TEAMS.keys()),
            format_func=lambda x: "전체 구단" if x == "전체" else str(TEAMS.get(x, x))
        )
    with col2:
        now = datetime.now()
        selected_month = st.selectbox(
            "월 선택",
            list(range(3, 11)),
            index=now.month - 3 if 3 <= now.month <= 10 else 0,
            format_func=lambda x: f"{x}월"
        )

    # 데이터 로드
    df = get_schedule(2025, selected_month)

    if df.empty:
        st.warning("해당 월의 경기 일정이 없습니다.")
        return

    df = preprocess_schedule(df)

    # 구단 필터링
    if selected_team != "전체":
        df = filter_by_team(df, selected_team)

    # 월별 경기 수 차트
    with st.expander("📊 일별 경기 수 보기", expanded=False):
        fig = draw_monthly_chart(df)
        st.plotly_chart(fig, use_container_width=True)

    # 예매 링크
    if selected_team != "전체":
        ticket_url = get_ticket_link(selected_team)
        team_name = TEAMS.get(selected_team, selected_team)
        st.markdown(
            f"### 🎟️ [{team_name} 티켓 예매 바로가기]({ticket_url})",
            unsafe_allow_html=False
        )
        st.divider()

    # 경기 일정 표시
    st.subheader(f"{selected_month}월 경기 일정 ({len(df)}경기)")
    draw_schedule_table(df)
