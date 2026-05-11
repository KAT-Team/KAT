"""
기상청 날씨 API 연동 모듈
- 공공데이터포털 기상청 단기예보 API 활용
- 경기장 위치 기반 날씨 예보 조회
"""

import requests
import os
from datetime import datetime, timedelta
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

# 하늘 상태 코드
SKY_CODE = {
    "1": "☀️ 맑음",
    "3": "⛅ 구름많음",
    "4": "☁️ 흐림"
}

# 강수 형태 코드
PTY_CODE = {
    "0": "없음",
    "1": "🌧️ 비",
    "2": "🌨️ 비/눈",
    "3": "❄️ 눈",
    "4": "🌦️ 소나기"
}


def _get_base_time(date: datetime) -> tuple:
    """
    기상청 API 기준 시간 계산
    발표 시간: 02, 05, 08, 11, 14, 17, 20, 23시
    """
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = date.hour

    base_time = "2300"
    base_date = (date - timedelta(days=1)).strftime("%Y%m%d")

    for t in reversed(base_times):
        if hour >= t:
            base_time = f"{t:02d}00"
            base_date = date.strftime("%Y%m%d")
            break

    return base_date, base_time


def get_weather(team: str, date: str) -> dict:
    """
    경기장 날씨 예보 조회
    :param team: 구단명 (예: "KIA")
    :param date: 날짜 (예: "20250501")
    :return: 날씨 정보 딕셔너리
    """
    if not WEATHER_API_KEY:
        return _get_mock_weather()

    grid = STADIUM_GRID.get(team, {"nx": 60, "ny": 127})
    now = datetime.now()
    base_date, base_time = _get_base_time(now)

    params = {
        "serviceKey": WEATHER_API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": grid["nx"],
        "ny": grid["ny"]
    }

    try:
        res = requests.get(WEATHER_API_URL, params=params, timeout=5)
        data = res.json()
        items = data['response']['body']['items']['item']

        # 예보 날짜 필터링
        target_date = date if date else datetime.now().strftime("%Y%m%d")
        target_items = [i for i in items if i['fcstDate'] == target_date]

        weather = {}
        for item in target_items:
            category = item['category']
            value = item['fcstValue']
            if category == 'TMP':
                weather['temp'] = f"{value}℃"
            elif category == 'POP':
                weather['rain_prob'] = int(value)
            elif category == 'SKY':
                weather['sky'] = SKY_CODE.get(value, "알 수 없음")
            elif category == 'PTY':
                weather['rain'] = PTY_CODE.get(value, "없음")
            elif category == 'REH':
                weather['humidity'] = f"{value}%"
            elif category == 'WSD':
                weather['wind'] = f"{value}m/s"

        return weather if weather else _get_mock_weather()

    except Exception as e:
        print(f"날씨 API 오류: {e}")
        return _get_mock_weather()


def _get_mock_weather() -> dict:
    """
    API 오류 시 기본값 반환
    """
    return {
        "temp": "정보 없음",
        "rain_prob": 0,
        "sky": "☀️ 맑음",
        "rain": "없음",
        "humidity": "정보 없음",
        "wind": "정보 없음"
    }


def get_rain_probability(team: str, date: str) -> int:
    """
    강수 확률 반환
    :param team: 구단명
    :param date: 날짜
    :return: 강수 확률 (0~100)
    """
    weather = get_weather(team, date)
    return weather.get("rain_prob", 0)


def get_weather_comment(rain_prob: int) -> str:
    """
    강수 확률에 따른 직관 추천 코멘트
    """
    if rain_prob >= 70:
        return "🌧️ 우천취소 가능성이 높습니다. 직관 전 공식 SNS를 확인하세요!"
    elif rain_prob >= 40:
        return "🌂 비 올 가능성이 있습니다. 우산을 챙기세요!"
    elif rain_prob >= 20:
        return "⛅ 흐릴 수 있습니다. 가볍게 겉옷을 챙기세요."
    else:
        return "☀️ 직관하기 좋은 날씨입니다!"
