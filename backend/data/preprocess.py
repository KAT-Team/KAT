"""
데이터 전처리 모듈
- 수집한 경기 일정 데이터 정제
- 날짜/시간 형식 통일
"""

import pandas as pd


def preprocess_schedule(df: pd.DataFrame) -> pd.DataFrame:
    """
    경기 일정 데이터 전처리
    :param df: 원본 경기 일정 DataFrame
    :return: 정제된 DataFrame
    """
    # TODO: 구현 필요
    return df


def filter_by_team(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    특정 구단 경기만 필터링
    :param df: 전체 경기 일정 DataFrame
    :param team: 구단명
    :return: 해당 구단 경기 DataFrame
    """
    # TODO: 구현 필요
    return df


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """
    날짜 범위로 경기 필터링
    :param df: 경기 일정 DataFrame
    :param start: 시작 날짜 (예: "2025-05-01")
    :param end: 종료 날짜 (예: "2025-05-31")
    :return: 필터링된 DataFrame
    """
    # TODO: 구현 필요
    return df
