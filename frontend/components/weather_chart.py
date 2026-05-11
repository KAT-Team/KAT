"""
날씨 시각화 컴포넌트
- 경기 당일 날씨 예보 시각화
- 강수 확률 게이지 차트
"""

import plotly.graph_objects as go


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
        title={"text": "강수 확률 (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 30],  "color": "lightgreen"},
                {"range": [30, 60], "color": "lightyellow"},
                {"range": [60, 100],"color": "lightcoral"},
            ]
        }
    ))
    return fig


def draw_weather_card(weather: dict) -> None:
    """
    날씨 정보 카드 출력 (Streamlit)
    :param weather: 날씨 딕셔너리
    """
    # TODO: 구현 필요
    pass
