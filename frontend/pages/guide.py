"""
직관 도우미 페이지
- 경기장 날씨 예보
- 교통 / 주차 정보
- 직관 체크리스트
- 원정 직관 가이드
"""

import streamlit as st
from backend.data.collect import TEAMS
from backend.data.stadium import get_stadium_info
from backend.data.weather import get_weather_comment


def show():
    st.header("🧭 직관 도우미")
    st.write("경기장 날씨, 교통, 준비물 정보를 한 번에 확인하세요!")

    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox(
            "관람할 경기 구단 (홈팀)",
            list(TEAMS.keys()),
            format_func=lambda x: str(TEAMS.get(x, x))
        )
    with col2:
        selected_date = st.date_input("경기 날짜")

    stadium = get_stadium_info(selected_team)

    if stadium:
        st.subheader(f"📍 {stadium.get('name', '')}")
        st.write(f"주소: {stadium.get('address', '')}")

        tab1, tab2, tab3, tab4 = st.tabs(["🌤️ 날씨", "🚌 교통/주차", "📋 체크리스트", "📖 원정 가이드"])

        with tab1:
            st.write("### 경기 당일 날씨 예보")
            # TODO: weather.py 연동 필요
            st.info("날씨 정보를 불러오는 중입니다...")
            comment = get_weather_comment(0)
            st.success(comment)

        with tab2:
            st.write("### 교통 및 주차 정보")
            parking = "✅ 주차 가능" if stadium.get("parking") else "❌ 주차 불가 (대중교통 이용 권장)"
            st.write(f"주차: {parking}")
            # TODO: 카카오맵 API 연동 필요
            st.info("교통 정보를 불러오는 중입니다...")

        with tab3:
            st.write("### 직관 체크리스트")
            # TODO: 날씨 기반 체크리스트 동적 생성 필요
            items = [
                "티켓 (모바일 or 실물)",
                "신분증",
                "응원 도구",
                "편한 신발",
                "간식 / 음료"
            ]
            for item in items:
                st.checkbox(item)

        with tab4:
            st.write("### 원정 직관 가이드")
            st.write(f"원정석 위치: {stadium.get('away_section', '정보 없음')}")
            # TODO: 구단별 응원 규칙, 반입 금지 물품 추가 필요
            st.info("원정 직관 상세 정보를 불러오는 중입니다...")
