"""
경기장 정보 모듈
- 구단별 경기장 주소, 좌석 정보, 편의시설
- 예매 링크, 원정 직관 가이드
"""


# 구단별 경기장 정보
STADIUM_INFO = {
    "KIA": {
        "name": "광주-기아 챔피언스 필드",
        "address": "광주광역시 북구 서림로 10",
        "lat": 35.168,
        "lng": 126.889,
        "capacity": 20500,
        "parking": True,
        "away_section": "3루 외야",
    },
    "Samsung": {
        "name": "대구 삼성 라이온즈 파크",
        "address": "대구광역시 수성구 야구전설로 1",
        "lat": 35.841,
        "lng": 128.682,
        "capacity": 24000,
        "parking": True,
        "away_section": "3루 외야",
    },
    "LG": {
        "name": "서울종합운동장 야구장 (잠실)",
        "address": "서울특별시 송파구 올림픽로 25",
        "lat": 37.512,
        "lng": 127.072,
        "capacity": 25000,
        "parking": True,
        "away_section": "3루 외야",
    },
    "Doosan": {
        "name": "서울종합운동장 야구장 (잠실)",
        "address": "서울특별시 송파구 올림픽로 25",
        "lat": 37.512,
        "lng": 127.072,
        "capacity": 25000,
        "parking": True,
        "away_section": "1루 외야",
    },
    "KT": {
        "name": "수원 KT 위즈 파크",
        "address": "경기도 수원시 장안구 경수대로 893",
        "lat": 37.300,
        "lng": 127.009,
        "capacity": 20000,
        "parking": True,
        "away_section": "3루 외야",
    },
    "SSG": {
        "name": "인천 SSG 랜더스 필드",
        "address": "인천광역시 미추홀구 매소홀로 618",
        "lat": 37.437,
        "lng": 126.693,
        "capacity": 23000,
        "parking": True,
        "away_section": "3루 외야",
    },
    "Lotte": {
        "name": "사직 야구장",
        "address": "부산광역시 동래구 사직로 45",
        "lat": 35.194,
        "lng": 129.061,
        "capacity": 24500,
        "parking": False,
        "away_section": "3루 외야",
    },
    "Hanwha": {
        "name": "한화생명 이글스 파크",
        "address": "대전광역시 중구 대종로 373",
        "lat": 36.317,
        "lng": 127.429,
        "capacity": 13000,
        "parking": True,
        "away_section": "3루 외야",
    },
    "NC": {
        "name": "창원 NC 파크",
        "address": "경상남도 창원시 마산회원구 삼호로 18",
        "lat": 35.222,
        "lng": 128.582,
        "capacity": 22112,
        "parking": True,
        "away_section": "3루 외야",
    },
    "Kiwoom": {
        "name": "고척 스카이돔",
        "address": "서울특별시 구로구 경인로 430",
        "lat": 37.498,
        "lng": 126.867,
        "capacity": 17000,
        "parking": False,
        "away_section": "3루 외야",
    },
}

# 좌석 등급 및 가격
SEAT_PRICES = {
    "KIA": {
        "테이블석": 70000,
        "프리미엄석": 55000,
        "중앙지정석": 16000,
        "내야지정석": 13000,
        "외야일반석": 9000,
    },
    # TODO: 나머지 구단 추가 필요
}


def get_stadium_info(team: str) -> dict:
    """
    경기장 정보 반환
    :param team: 구단명 (예: "KIA")
    :return: 경기장 정보 딕셔너리
    """
    return STADIUM_INFO.get(team, {})


def get_seat_prices(team: str) -> dict:
    """
    좌석 가격 반환
    :param team: 구단명
    :return: 좌석 등급별 가격 딕셔너리
    """
    return SEAT_PRICES.get(team, {})


def get_all_stadiums() -> list:
    """
    전체 경기장 목록 반환
    :return: 경기장 정보 리스트
    """
    return [
        {"team": team, **info}
        for team, info in STADIUM_INFO.items()
    ]
