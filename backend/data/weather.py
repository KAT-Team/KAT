"""
기상청 날씨 API 연동 모듈
- 공공데이터포털 기상청 단기예보 API 활용
- 경기장 위치 기반 날씨 예보 조회
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# 경기장별 기상청 격자 좌표 (nx, ny)
STADIUM_GRID = {
    "KIA":     {"nx": 58, "ny": 74},
    "Samsung": {"nx": 89, "ny": 90},
    "LG":      {"nx": 61, "ny": 126},
    "Doosan":  {"nx": 61, "ny": 126},
    "KT":      {"nx": 60, "ny": 121},
    "SSG":     {"nx": 54, "ny": 124},
    "Lotte":   {"nx": 98, "ny": 76},
    "Hanwha":  {"nx": 67, "ny": 100},
    "NC":      {"nx": 90, "ny": 79},
    "Kiwoom":  {"nx": 58, "ny": 125},
}


def get_weather(team: str, date: str) -> dict:
    """
    경기장 날씨 예보 조회
    :param team: 구단명 (예: "KIA")
    :param date: 날짜 (예: "20250501")
    :return: {
        "temp": 22,
        "rain_prob": 30,
        "sky": "구름많음",
        "rain": "없음",
        "humidity": 60,
        "wind": 3.2
    }
    """
    # TODO: 구현 필요
    return {}


def get_rain_probability(team: str, date: str) -> int:
    """
    강수 확률 반환
    :param team: 구단명
    :param date: 날짜
    :return: 강수 확률 (0~100)
    """
    # TODO: 구현 필요
    weather = get_weather(team, date)
    return weather.get("rain_prob", 0)


def get_weather_comment(rain_prob: int) -> str:
    """
    강수 확률에 따른 직관 추천 코멘트
    :param rain_prob: 강수 확률
    :return: 코멘트 문자열
    """
    if rain_prob >= 70:
        return "🌧️ 우천취소 가능성이 높습니다. 직관 전 공식 SNS를 확인하세요!"
    elif rain_prob >= 40:
        return "🌂 비 올 가능성이 있습니다. 우산을 챙기세요!"
    elif rain_prob >= 20:
        return "⛅ 흐릴 수 있습니다. 가볍게 겉옷을 챙기세요."
    else:
        return "☀️ 직관하기 좋은 날씨입니다!"
