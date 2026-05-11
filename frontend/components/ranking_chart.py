"""
순위표 차트 컴포넌트
- KBO 구단 순위 시각화
"""

import plotly.graph_objects as go
import pandas as pd


# 샘플 순위 데이터 (실제 데이터로 교체 필요)
SAMPLE_RANKING = pd.DataFrame({
    'rank':     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'team':     ['KIA', 'Samsung', 'LG', 'KT', 'SSG', 'Lotte', 'Doosan', 'Hanwha', 'NC', 'Kiwoom'],
    'win':      [30, 28, 26, 25, 24, 22, 20, 18, 16, 14],
    'lose':     [14, 16, 18, 19, 20, 22, 24, 26, 28, 30],
    'draw':     [0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
    'win_rate': [0.682, 0.636, 0.591, 0.568, 0.545, 0.500, 0.455, 0.409, 0.364, 0.318]
})


def get_ranking_data() -> pd.DataFrame:
    """
    순위 데이터 반환
    실제 크롤링 구현 전까지 샘플 데이터 사용
    """
    return SAMPLE_RANKING


def draw_ranking_table(ranking_df: pd.DataFrame) -> go.Figure:
    """
    순위표 테이블 시각화
    :param ranking_df: 순위 DataFrame
    :return: plotly Figure 객체
    """
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['순위', '팀', '승', '패', '무', '승률'],
            fill_color='#1f4e79',
            font=dict(color='white', size=13),
            align='center',
            height=35
        ),
        cells=dict(
            values=[
                ranking_df['rank'],
                ranking_df['team'],
                ranking_df['win'],
                ranking_df['lose'],
                ranking_df['draw'],
                ranking_df['win_rate'].apply(lambda x: f"{x:.3f}")
            ],
            fill_color=[['#f0f8ff' if i % 2 == 0 else 'white'
                         for i in range(len(ranking_df))]],
            align='center',
            height=30,
            font=dict(size=12)
        )
    )])

    fig.update_layout(
        title="KBO 현재 순위",
        height=400,
        margin=dict(t=50, b=0)
    )

    return fig


def draw_win_rate_chart(ranking_df: pd.DataFrame) -> go.Figure:
    """
    구단별 승률 바 차트
    :param ranking_df: 순위 DataFrame
    :return: plotly Figure 객체
    """
    colors = ['gold' if r == 1 else 'silver' if r == 2 else
              '#cd7f32' if r == 3 else '#4a90d9'
              for r in ranking_df['rank']]

    fig = go.Figure(go.Bar(
        x=ranking_df['team'],
        y=ranking_df['win_rate'],
        text=ranking_df['win_rate'].apply(lambda x: f"{x:.3f}"),
        textposition='auto',
        marker_color=colors
    ))

    fig.update_layout(
        title="구단별 승률",
        xaxis_title="구단",
        yaxis_title="승률",
        height=350,
        yaxis=dict(range=[0, 1])
    )

    return fig
