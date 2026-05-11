"""
좌석 가격 비교 컴포넌트
- 구단별 좌석 등급 및 가격 비교 차트
"""

import plotly.graph_objects as go
from backend.data.stadium import get_seat_prices


def draw_seat_price_chart(team: str) -> go.Figure:
    """
    좌석 가격 비교 바 차트
    :param team: 구단명
    :return: plotly Figure 객체
    """
    prices = get_seat_prices(team)

    fig = go.Figure(go.Bar(
        x=list(prices.keys()),
        y=list(prices.values()),
        text=list(prices.values()),
        textposition="auto"
    ))

    fig.update_layout(
        title=f"{team} 좌석 등급별 가격",
        xaxis_title="좌석 등급",
        yaxis_title="가격 (원)"
    )

    return fig
