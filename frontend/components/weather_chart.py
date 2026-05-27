"""
날씨 시각화 컴포넌트
- 강수 확률 게이지 차트
- 날씨 정보 카드 (KAT 디자인 적용)
"""

import os
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# 1. .env 파일의 내용을 환경 변수로 불러옵니다
load_dotenv()

# 2. os.getenv를 사용해 금고(env)에서 키를 꺼냅니다
API_KEY = os.getenv("OPENWEATHER_API_KEY")  # .env에 적은 변수명과 똑같아야 함


# ===== KAT 컬러 테마 =====
KAT_NAVY = "#5B6584"          # 메인 네이비
KAT_NAVY_LIGHT = "#8590A8"    # 밝은 네이비
KAT_BG_LIGHT = "#F5F6FA"      # 카드 배경
KAT_TEXT = "#2C3144"          # 메인 텍스트


def draw_rain_gauge(rain_prob: int) -> go.Figure:
    """
    강수 확률 게이지 차트 (KAT 디자인 적용)
    :param rain_prob: 강수 확률 (0~100)
    :return: plotly Figure 객체
    """
    # 단계별 바 색상
    if rain_prob >= 70:
        bar_color = "#E74C3C"   # 빨강
    elif rain_prob >= 40:
        bar_color = "#F39C12"   # 주황
    else:
        bar_color = "#27AE60"   # 초록

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rain_prob,
        number={
            "suffix": "%",
            "font": {"size": 44, "color": KAT_TEXT},
        },
        title={
            "text": "<b>강수 확률</b>",
            "font": {"size": 18, "color": KAT_NAVY},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": KAT_NAVY_LIGHT,
                "tickfont": {"size": 11, "color": KAT_NAVY_LIGHT},
            },
            "bar": {"color": bar_color, "thickness": 0.7},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": KAT_BG_LIGHT,
            "steps": [
                {"range": [0, 30],   "color": "#E8F5E9"},   # 연한 초록
                {"range": [30, 60],  "color": "#FFF8E1"},   # 연한 노랑
                {"range": [60, 100], "color": "#FFEBEE"},   # 연한 빨강
            ],
            "threshold": {
                "line": {"color": "#C0392B", "width": 4},
                "thickness": 0.8,
                "value": 70,
            },
        },
    ))

    fig.update_layout(
        height=300,
        margin=dict(t=60, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": KAT_TEXT, "family": "Arial"},
    )
    return fig


def _metric_card(icon: str, label: str, value: str, accent_color: str) -> str:
    """
    개별 메트릭 카드 HTML 생성 (내부 함수)
    :param accent_color: 상단 액센트 컬러 바 색상
    """
    # 값이 "정보 없음"이면 흐릿하게 표시
    value_color = KAT_NAVY_LIGHT if value == "정보 없음" else KAT_TEXT
    value_size = "14px" if value == "정보 없음" else "20px"

    return f"""
    <div style="
        background: #FFFFFF;
        border-radius: 12px;
        border-top: 4px solid {accent_color};
        border-left: 1px solid #E8EAF1;
        border-right: 1px solid #E8EAF1;
        border-bottom: 1px solid #E8EAF1;
        padding: 18px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(91, 101, 132, 0.12);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.2s, box-shadow 0.2s;
    ">
        <div style="font-size: 32px; margin-bottom: 6px;">{icon}</div>
        <div style="font-size: 13px; color: {KAT_NAVY_LIGHT};
                    margin-bottom: 6px; font-weight: 500;">{label}</div>
        <div style="font-size: {value_size}; color: {value_color};
                    font-weight: 700;">{value}</div>
    </div>
    """


def draw_weather_card(weather: dict) -> None:
    """
    날씨 정보 카드 출력 (KAT 디자인 - 5열 그리드, 의미별 컬러 액센트)
    강수 확률은 별도 게이지에서 표시하므로 5개 정보만 카드로 보여줌
    :param weather: 날씨 딕셔너리
    """
    cols = st.columns(5)

    # (아이콘, 라벨, 값, 액센트 컬러)
    items = [
        ("🌡️", "기온",      weather.get("temp", "정보 없음"),     "#FF6B6B"),  # 따뜻한 빨강
        ("🌤️", "하늘 상태", weather.get("sky", "정보 없음"),       "#FFA94D"),  # 부드러운 주황
        ("💨", "풍속",      weather.get("wind", "정보 없음"),      "#4DABF7"),  # 시원한 파랑
        ("💧", "습도",      weather.get("humidity", "정보 없음"),  "#06A77D"),  # 청록
        ("🌧️", "강수 형태", weather.get("rain", "없음"),           "#845EC2"),  # 보라
    ]

    for col, (icon, label, value, color) in zip(cols, items):
        with col:
            st.markdown(
                _metric_card(icon, label, str(value), color),
                unsafe_allow_html=True,
            )
