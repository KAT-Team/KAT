"""
좌석 가격 비교 컴포넌트
- 구단별 좌석 등급 및 가격 비교 차트
"""

import plotly.graph_objects as go
import streamlit as st
from backend.data.stadium import get_seat_prices, STADIUM_INFO


def draw_seat_price_chart(team: str) -> go.Figure:
    """
    좌석 가격 비교 바 차트
    :param team: 구단명
    :return: plotly Figure 객체
    """
    prices = get_seat_prices(team)

    if not prices:
        fig = go.Figure()
        fig.update_layout(title="좌석 가격 정보가 없습니다.")
        return fig

    fig = go.Figure(go.Bar(
        x=list(prices.keys()),
        y=list(prices.values()),
        text=[f"{v:,}원" for v in prices.values()],
        textposition="auto",
        marker_color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    ))

    fig.update_layout(
        title=f"{team} 좌석 등급별 가격",
        xaxis_title="좌석 등급",
        yaxis_title="가격 (원)",
        height=350,
        yaxis=dict(tickformat=",")
    )

    return fig


def draw_seat_comparison(teams: list) -> go.Figure:
    """
    여러 구단 좌석 가격 비교 차트
    :param teams: 구단명 리스트
    :return: plotly Figure 객체
    """
    fig = go.Figure()

    for team in teams:
        prices = get_seat_prices(team)
        if prices:
            fig.add_trace(go.Bar(
                name=team,
                x=list(prices.keys()),
                y=list(prices.values()),
                text=[f"{v:,}원" for v in prices.values()],
                textposition="auto"
            ))

    fig.update_layout(
        title="구단별 좌석 가격 비교",
        xaxis_title="좌석 등급",
        yaxis_title="가격 (원)",
        barmode="group",
        height=400,
        yaxis=dict(tickformat=",")
    )

    return fig
