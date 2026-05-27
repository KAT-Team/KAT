"""
캘린더 컴포넌트
- 경기 일정을 테이블 형태로 시각화
- plotly 활용
"""

import os
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from backend.data.collect import TEAMS

# 구단별 색상
TEAM_COLORS = {
    "KIA":     "#EA0029",
    "Samsung": "#074CA1",
    "LG":      "#C30452",
    "Doosan":  "#131230",
    "KT":      "#000000",
    "SSG":     "#CE0E2D",
    "Lotte":   "#002058",
    "Hanwha":  "#FF6600",
    "NC":      "#071D49",
    "Kiwoom":  "#820024"
}

TEAM_LOGOS = {
    "KIA":     "logo_kia.svg",
    "Samsung": "logo_samsung.svg",
    "LG":      "logo_lg.svg",
    "Doosan":  "logo_doosan.svg",
    "KT":      "logo_kt.svg",
    "SSG":     "logo_ssg.svg",
    "Lotte":   "logo_lotte.svg",
    "Hanwha":  "logo_hanwha.svg",
    "NC":      "logo_nc.svg",
    "Kiwoom":  "logo_kiwoom.svg"
}


def draw_schedule_table(schedule_df: pd.DataFrame) -> None:
    """
    경기 일정 테이블 출력 (구글 스타일 페이지 버튼 + 500px SVG 짤림/정렬 해결 버전)
    """
    if schedule_df.empty:
        st.info("해당 기간에 경기가 없습니다.")
        return

    weeks = ['월', '화', '수', '목', '금', '토', '일']
    LOGO_DIR = "frontend/assets"

    # 💡 st.image 컴포넌트를 컬럼 내부에서 무조건 가운데 정렬시키는 CSS 주입
    st.markdown(
        """
        <style>
            [data-testid="stImage"] {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # 💡 [핵심 도입] 구글 스타일 하단 페이지 번호용 계산
    # ==========================================================
    ITEMS_PER_PAGE = 20  # 한 화면에 보여줄 경기 수 (버튼 수에 맞춰 20개로 상향 조정)
    total_games = len(schedule_df)
    total_pages = max(((total_games - 1) // ITEMS_PER_PAGE) + 1, 1)

    # 현재 선택된 페이지를 저장할 세션 상태 초기화 (기본값: 1페이지)
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # 안전장치: 전체 페이지 수가 줄어들었을 경우 현재 페이지 조정
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
    # ==========================================================

    # 상단에 "현재 페이지 데이터" 슬라이싱
    start_row = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
    end_row = start_row + ITEMS_PER_PAGE
    page_df = schedule_df.iloc[start_row:end_row]

    # 경기 일정 렌더링 영역
    with st.container():
        for idx, row in page_df.iterrows():
            home = row['home_team']
            away = row['away_team']

            home_color = TEAM_COLORS.get(home, "#333333")
            away_color = TEAM_COLORS.get(away, "#333333")
            home_name = TEAMS.get(home, home)
            away_name = TEAMS.get(away, away)

            away_logo_path = os.path.join(LOGO_DIR, TEAM_LOGOS.get(away, ""))
            home_logo_path = os.path.join(LOGO_DIR, TEAM_LOGOS.get(home, ""))

            try:
                date = pd.to_datetime(row['date'])
                date_str = f"**{date.strftime('%m/%d')}** ({weeks[date.weekday()]})"
            except:
                date_str = f"**{row['date']}**"

            # 8개 컬럼 구조 및 순서 유지
            (col_date, col_time, col_stadium, col_away_name, col_away_logo,
             col_vs, col_home_logo, col_home_name) = st.columns([0.5, 0.5, 0.5, 1, 0.2, 0.6, 0.2, 2])

            with col_date:
                st.write(date_str)

            with col_time:
                st.write(f"{row['time']}")

            with col_stadium:
                st.write(f"{row['stadium']}")

            with col_away_name:
                st.markdown(f"<div style='text-align: right; color:{away_color}; font-weight:bold; font-size:15px; padding-top:2px;'>{away_name}</div>", unsafe_allow_html=True)

            with col_away_logo:
                if os.path.exists(away_logo_path):
                    st.image(away_logo_path, width=26)
                else:
                    st.write("⚾")

            with col_vs:
                st.markdown("<div style='text-align: center; color:#888; font-weight:bold; padding-top:2px;'>vs</div>", unsafe_allow_html=True)

            with col_home_logo:
                if os.path.exists(home_logo_path):
                    st.image(home_logo_path, width=26)
                else:
                    st.write("🏠")

            with col_home_name:
                st.markdown(f"<div style='text-align: left; color:{home_color}; font-weight:bold; font-size:15px; padding-top:2px;'>{home_name}</div>", unsafe_allow_html=True)

            st.divider()

    # ==========================================================
    # 💡 [핵심 도입] 하단 구글 스타일 페이지네이션 버튼 바
    # ==========================================================
    st.write("")  # 테이블과의 간격 확보

    # 버튼들을 가로로 나열하기 위해 페이지 수만큼 컬럼을 생성합니다.
    # 양옆 여백을 주어 정중앙에 예쁘게 모이도록 빈 컬럼(spacer)을 배치합니다.
    spacer_left, *btn_cols, spacer_right = st.columns([3] + [1] * total_pages + [3])

    for i, col in enumerate(btn_cols):
        page_num = i + 1
        with col:
            # 현재 선택된 페이지는 눈에 띄게 'primary' 테마 색상을 적용합니다.
            is_current = (page_num == st.session_state.current_page)
            btn_type = "primary" if is_current else "secondary"

            # 숫자 버튼 생성
            if st.button(f"{page_num}", key=f"page_btn_{page_num}", type=btn_type, use_container_width=True):
                st.session_state.current_page = page_num
                st.rerun()  # 페이지 번호가 바뀌었으므로 즉시 화면 재렌더링


def draw_monthly_chart(schedule_df: pd.DataFrame) -> go.Figure:
    """
    월별 경기 수 바 차트
    """
    if schedule_df.empty:
        return go.Figure()

    df = schedule_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    daily_counts = df.groupby(df['date'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']

    fig = go.Figure(go.Bar(
        x=daily_counts['date'].astype(str),
        y=daily_counts['count'],
        marker_color='#1f77b4',
        text=daily_counts['count'],
        textposition='auto'
    ))

    fig.update_layout(
        title="일별 경기 수",
        xaxis_title="날짜",
        yaxis_title="경기 수",
        height=300
    )

    return fig
