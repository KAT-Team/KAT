"""
KBO 경기 일정 수집 모듈
- KBO 공식 사이트 크롤링
- requests + BeautifulSoup 활용
"""

import requests
from bs4 import BeautifulSoup
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
    "KIA":     "https://www.tigersticket.co.kr",
    "Samsung": "https://ticket.samsung.com/lions",
    "LG":      "https://www.lgtwins.com/ticket",
    "Doosan":  "https://ticket.doosanbears.com",
    "KT":      "https://www.ktwiz.co.kr/ticket",
    "SSG":     "https://www.ssglanders.com/ticket",
    "Lotte":   "https://ticket.lottegem.com",
    "Hanwha":  "https://www.hanwhaeagles.co.kr/ticket",
    "NC":      "https://www.ncdinos.com/ticket",
    "Kiwoom":  "https://www.heroesbaseball.co.kr/ticket"
}


def get_schedule(year: int, month: int) -> pd.DataFrame:
    """
    KBO 경기 일정 수집
    :param year: 연도 (예: 2025)
    :param month: 월 (예: 5)
    :return: 경기 일정 DataFrame
    컬럼: date, home_team, away_team, stadium, time
    """
    # TODO: 구현 필요
    return pd.DataFrame()


def get_ticket_link(team: str) -> str:
    """
    구단별 예매 링크 반환
    :param team: 구단명 (예: "KIA")
    :return: 예매 링크 URL
    """
    return TICKET_LINKS.get(team, "")


def get_recent_results(team: str, n: int = 5) -> pd.DataFrame:
    """
    최근 경기 결과 수집
    :param team: 구단명
    :param n: 최근 n경기
    :return: 경기 결과 DataFrame
    """
    # TODO: 구현 필요
    return pd.DataFrame()
