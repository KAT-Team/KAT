"""
순위표 차트 컴포넌트
- KBO 구단 순위 시각화
"""

import plotly.graph_objects as go
import pandas as pd


def draw_ranking_table(ranking_df: pd.DataFrame) -> go.Figure:
    """
    순위표 테이블 시각화
    :param ranking_df: 순위 DataFrame
    컬럼: rank, team, win, lose, draw, win_rate
    :return: plotly Figure 객체
    """
    # TODO: 구현 필요
    fig = go.Figure()
    return fig


def draw_win_rate_chart(ranking_df: pd.DataFrame) -> go.Figure:
    """
    구단별 승률 바 차트
    :param ranking_df: 순위 DataFrame
    :return: plotly Figure 객체
    """
    # TODO: 구현 필요
    fig = go.Figure()
    return fig
