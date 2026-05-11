"""
캘린더 컴포넌트
- 경기 일정을 캘린더 형태로 시각화
- plotly 활용
"""

import plotly.graph_objects as go
import pandas as pd


def draw_calendar(schedule_df: pd.DataFrame) -> go.Figure:
    """
    경기 일정 캘린더 시각화
    :param schedule_df: 경기 일정 DataFrame
    컬럼: date, home_team, away_team, stadium, time
    :return: plotly Figure 객체
    """
    # TODO: 구현 필요
    fig = go.Figure()
    return fig


def draw_schedule_table(schedule_df: pd.DataFrame) -> None:
    """
    경기 일정 테이블 출력 (Streamlit)
    :param schedule_df: 경기 일정 DataFrame
    """
    # TODO: 구현 필요
    pass
