"""
캘린더 컴포넌트
- 경기 일정을 테이블 형태로 시각화
- plotly 활용
"""

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


def draw_schedule_table(schedule_df: pd.DataFrame) -> None:
    """
    경기 일정 테이블 출력
    :param schedule_df: 경기 일정 DataFrame
    """
    if schedule_df.empty:
        st.info("해당 기간에 경기가 없습니다.")
        return

    for _, row in schedule_df.iterrows():
        home = row['home_team']
        away = row['away_team']
        home_color = TEAM_COLORS.get(home, "#333333")
        away_color = TEAM_COLORS.get(away, "#333333")
        home_name = TEAMS.get(home, home)
        away_name = TEAMS.get(away, away)

        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
        with col1:
            date = pd.to_datetime(row['date'])
            st.write(f"**{date.strftime('%m/%d')}** ({['월','화','수','목','금','토','일'][date.weekday()]})")
        with col2:
            st.write(f"🕡 {row['time']}")
        with col3:
            st.markdown(
                f"<span style='color:{home_color};font-weight:bold'>{home_name}</span> vs "
                f"<span style='color:{away_color};font-weight:bold'>{away_name}</span>",
                unsafe_allow_html=True
            )
        with col4:
            st.write(f"📍 {row['stadium']}")
        with col5:
            st.write("")

        st.divider()


def draw_monthly_chart(schedule_df: pd.DataFrame) -> go.Figure:
    """
    월별 경기 수 바 차트
    :param schedule_df: 경기 일정 DataFrame
    :return: plotly Figure 객체
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
