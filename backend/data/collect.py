"""
KBO 경기 일정 수집 모듈
- CSV 파일에서 경기 일정 데이터 로드
- 구단별 예매 링크 제공
"""

import os
import pandas as pd


# KBO 10개 구단 정보
TEAMS = {
    "KIA":     "기아 타이거즈",
    "Samsung": "삼성 라이온즈",
    "LG":      "LG 트윈스",
    "Doosan":  "두산 베어스",
    "KT":      "KT 위즈",
    "SSG":     "SSG 랜더스",
    "Lotte":   "롯데 자이언츠",
    "Hanwha":  "한화 이글스",
    "NC":      "NC 다이노스",
    "Kiwoom":  "키움 히어로즈"
}

# 구단별 예매 링크
TICKET_LINKS = {
        "KIA": "https://www.ticketlink.co.kr/sports/137/58",
        "삼성": "https://www.ticketlink.co.kr/sports/137/57",
        "LG": "https://www.ticketlink.co.kr/sports/137/59",
        "두산": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB004",
        "KT": "https://www.ticketlink.co.kr/sports/137/62",
        "SSG": "https://ticket.ssg.com/ticket",
        "롯데": "https://ticket.giantsclub.com/loginForm.do",
        "한화": "https://www.ticketlink.co.kr/sports/137/63",
        "NC": "https://www.ncdinos.com/auth/ticket.do",
        "키움": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003"
    }

# CSV 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "static", "schedule_2025.csv")


def get_schedule(year: int, month: int) -> pd.DataFrame:
    """
    경기 일정 반환
    :param year: 연도 (예: 2025)
    :param month: 월 (예: 5)
    :return: 경기 일정 DataFrame
    컬럼: date, time, home_team, away_team, stadium
    """
    try:
        df = pd.read_csv(CSV_PATH)
        df['date'] = pd.to_datetime(df['date'])
        result = df[
            (df['date'].dt.year == year) &
            (df['date'].dt.month == month)
        ].copy()
        result = result.sort_values('date').reset_index(drop=True)
        return result
    except FileNotFoundError:
        print(f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}")
        return pd.DataFrame(
            columns=['date', 'time', 'home_team', 'away_team', 'stadium']
        )
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return pd.DataFrame(
            columns=['date', 'time', 'home_team', 'away_team', 'stadium']
        )


def get_all_schedule(year: int) -> pd.DataFrame:
    """
    연간 전체 경기 일정 반환
    :param year: 연도
    :return: 전체 경기 일정 DataFrame
    """
    try:
        df = pd.read_csv(CSV_PATH)
        df['date'] = pd.to_datetime(df['date'])
        result = df[df['date'].dt.year == year].copy()
        result = result.sort_values('date').reset_index(drop=True)
        return result
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return pd.DataFrame(
            columns=['date', 'time', 'home_team', 'away_team', 'stadium']
        )


def get_team_schedule(team: str, year: int, month: int | None = None) -> pd.DataFrame:
    """
    특정 구단 경기 일정 반환
    :param team: 구단명 (예: "KIA")
    :param year: 연도
    :param month: 월 (None이면 전체 시즌)
    :return: 해당 구단 경기 DataFrame
    """
    df = get_all_schedule(year)
    if df.empty:
        return df

    team_df = df[
        (df['home_team'] == team) |
        (df['away_team'] == team)
    ].copy()

    if month:
        team_df = team_df[team_df['date'].dt.month == month]

    return team_df.reset_index(drop=True)


def get_ticket_link(team: str) -> str:
    """
    구단별 예매 링크 반환
    :param team: 구단명 (예: "KIA")
    :return: 예매 링크 URL
    """
    return TICKET_LINKS.get(team, "")


def get_today_games() -> pd.DataFrame:
    """
    오늘 경기 반환
    :return: 오늘 경기 DataFrame
    """
    today = pd.Timestamp.now().normalize()
    df = get_all_schedule(today.year)
    if df.empty:
        return df
    return df[df['date'] == today].reset_index(drop=True)
