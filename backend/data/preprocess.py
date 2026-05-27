"""
데이터 전처리 모듈
- 수집한 경기 일정 데이터 정제
- 날짜/시간 형식 통일
- 필터링 함수 제공
"""

import pandas as pd


def preprocess_schedule(df: pd.DataFrame) -> pd.DataFrame:
    """
    경기 일정 데이터 전처리
    :param df: 원본 경기 일정 DataFrame
    :return: 정제된 DataFrame
    """
    if df.empty:
        return df

    df = df.copy()

    # 날짜 형식 통일
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

    # 요일 추가
    df['weekday'] = df['date'].dt.day_name(locale='ko_KR').str[:1]

    # 날짜 표시용 문자열 추가 (예: 05/01 (목))
    df['date_str'] = df['date'].dt.strftime('%m/%d') + ' (' + df['weekday'] + ')'

    # 결측값 처리
    df['time'] = df['time'].fillna('18:30')
    df['stadium'] = df['stadium'].fillna('미정')

    # 정렬
    df = df.sort_values(['date', 'time']).reset_index(drop=True)

    return df


def filter_by_team(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """
    특정 구단 경기만 필터링
    :param df: 전체 경기 일정 DataFrame
    :param team: 구단명 (예: "KIA")
    :return: 해당 구단 경기 DataFrame
    """
    if df.empty or team == "전체":
        return df

    return df[
        (df['home_team'] == team) |
        (df['away_team'] == team)
    ].reset_index(drop=True)


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """
    날짜 범위로 경기 필터링
    :param df: 경기 일정 DataFrame
    :param start: 시작 날짜 (예: "2025-05-01")
    :param end: 종료 날짜 (예: "2025-05-31")
    :return: 필터링된 DataFrame
    """
    if df.empty:
        return df

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    return df[
        (df['date'] >= start_dt) &
        (df['date'] <= end_dt)
    ].reset_index(drop=True)


def filter_by_month(df: pd.DataFrame, month: int) -> pd.DataFrame:
    """
    월별 경기 필터링
    :param df: 경기 일정 DataFrame
    :param month: 월 (예: 5)
    :return: 필터링된 DataFrame
    """
    if df.empty:
        return df

    return df[df['date'].dt.month == month].reset_index(drop=True)


def get_schedule_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    화면에 표시할 형태로 변환
    :param df: 경기 일정 DataFrame
    :return: 표시용 DataFrame
    """
    if df.empty:
        return df

    df = preprocess_schedule(df)

    display_df = pd.DataFrame({
        '날짜': df['date_str'],
        '시간': df['time'],
        '홈팀': df['home_team'],
        '원정팀': df['away_team'],
        '구장': df['stadium']
    })

    return display_df
