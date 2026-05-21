"""
날씨 시각화 컴포넌트
- 강수 확률 게이지 차트
- 날씨 정보 카드
"""

import os
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# 1. .env 파일의 내용을 환경 변수로 불러옵니다
load_dotenv()

# 2. os.getenv를 사용해 금고(env)에서 키를 꺼냅니다
API_KEY = os.getenv("OPENWEATHER_API_KEY") # .env에 적은 변수명과 똑같아야 함


def draw_rain_gauge(rain_prob: int) -> go.Figure:
    """
    강수 확률 게이지 차트
    :param rain_prob: 강수 확률 (0~100)
    :return: plotly Figure 객체
    """
    color = "red" if rain_prob >= 70 else "orange" if rain_prob >= 40 else "green"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rain_prob,
        number={"suffix": "%"},
        title={"text": "강수 확률"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 30],  "color": "#e8f5e9"},
                {"range": [30, 60], "color": "#fff8e1"},
                {"range": [60, 100],"color": "#ffebee"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 70
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(t=50, b=0))
    return fig


def draw_weather_card(weather: dict) -> None:
    """
    날씨 정보 카드 출력
    :param weather: 날씨 딕셔너리
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ 기온", weather.get("temp", "정보 없음"))
        st.metric("💧 습도", weather.get("humidity", "정보 없음"))

    with col2:
        st.metric("🌤️ 하늘 상태", weather.get("sky", "정보 없음"))
        st.metric("🌧️ 강수 형태", weather.get("rain", "없음"))

    with col3:
        st.metric("💨 풍속", weather.get("wind", "정보 없음"))
        rain_prob = weather.get("rain_prob", 0)
        st.metric("☔ 강수 확률", f"{rain_prob}%")




