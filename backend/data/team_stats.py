"""
KBO 팀 스탯 및 선발투수 데이터 모듈
- 10개 구단 팀 승률, 타율 등 스탯 데이터
- 구단별 주요 선발투수 목록
- 실제 데이터로 주기적 업데이트 필요
"""

# 10개 구단 팀 스탯 (2025 시즌 기준)
# win_rate: 팀 승률
# avg: 팀 타율
# era: 팀 평균자책점
# ops: 팀 OPS
TEAM_STATS = {
    "KIA": {
        "win_rate": 0.582,
        "avg": 0.291,
        "era": 3.85,
        "ops": 0.821,
        "home_advantage": 0.03
    },
    "Samsung": {
        "win_rate": 0.534,
        "avg": 0.278,
        "era": 4.12,
        "ops": 0.798,
        "home_advantage": 0.03
    },
    "LG": {
        "win_rate": 0.556,
        "avg": 0.285,
        "era": 3.92,
        "ops": 0.812,
        "home_advantage": 0.03
    },
    "Doosan": {
        "win_rate": 0.489,
        "avg": 0.272,
        "era": 4.45,
        "ops": 0.781,
        "home_advantage": 0.03
    },
    "KT": {
        "win_rate": 0.512,
        "avg": 0.276,
        "era": 4.21,
        "ops": 0.789,
        "home_advantage": 0.03
    },
    "SSG": {
        "win_rate": 0.523,
        "avg": 0.279,
        "era": 4.08,
        "ops": 0.801,
        "home_advantage": 0.03
    },
    "Lotte": {
        "win_rate": 0.478,
        "avg": 0.269,
        "era": 4.67,
        "ops": 0.774,
        "home_advantage": 0.03
    },
    "Hanwha": {
        "win_rate": 0.467,
        "avg": 0.265,
        "era": 4.89,
        "ops": 0.768,
        "home_advantage": 0.03
    },
    "NC": {
        "win_rate": 0.501,
        "avg": 0.274,
        "era": 4.34,
        "ops": 0.785,
        "home_advantage": 0.03
    },
    "Kiwoom": {
        "win_rate": 0.456,
        "avg": 0.262,
        "era": 4.98,
        "ops": 0.761,
        "home_advantage": 0.03
    }
}

# 구단별 주요 선발투수 목록
# name: 투수 이름
# era: 평균자책점 (낮을수록 좋음)
# whip: 이닝당 출루 허용률 (낮을수록 좋음)
# k_rate: 탈삼진율
PITCHERS = {
    "KIA": [
        {"name": "양현종", "era": 3.12, "whip": 1.15, "k_rate": 0.24},
        {"name": "네일",   "era": 3.45, "whip": 1.22, "k_rate": 0.26},
        {"name": "윤영철", "era": 4.21, "whip": 1.38, "k_rate": 0.20},
        {"name": "이의리", "era": 3.89, "whip": 1.29, "k_rate": 0.22},
        {"name": "황동하", "era": 4.56, "whip": 1.45, "k_rate": 0.18},
    ],
    "Samsung": [
        {"name": "원태인", "era": 3.21, "whip": 1.18, "k_rate": 0.25},
        {"name": "뷰캐넌", "era": 3.78, "whip": 1.25, "k_rate": 0.23},
        {"name": "백정현", "era": 4.34, "whip": 1.41, "k_rate": 0.19},
        {"name": "최채흥", "era": 4.12, "whip": 1.33, "k_rate": 0.21},
        {"name": "레예스", "era": 3.56, "whip": 1.21, "k_rate": 0.27},
    ],
    "LG": [
        {"name": "엔스",   "era": 3.34, "whip": 1.19, "k_rate": 0.26},
        {"name": "임찬규", "era": 3.67, "whip": 1.24, "k_rate": 0.23},
        {"name": "켈리",   "era": 3.89, "whip": 1.28, "k_rate": 0.24},
        {"name": "최원태", "era": 4.23, "whip": 1.37, "k_rate": 0.20},
        {"name": "플럿코", "era": 4.01, "whip": 1.31, "k_rate": 0.22},
    ],
    "Doosan": [
        {"name": "알칸타라", "era": 3.56, "whip": 1.23, "k_rate": 0.25},
        {"name": "이영하",   "era": 4.12, "whip": 1.35, "k_rate": 0.21},
        {"name": "곽빈",     "era": 4.45, "whip": 1.42, "k_rate": 0.19},
        {"name": "김택연",   "era": 4.78, "whip": 1.51, "k_rate": 0.17},
        {"name": "홍건희",   "era": 4.34, "whip": 1.39, "k_rate": 0.20},
    ],
    "KT": [
        {"name": "고영표", "era": 3.45, "whip": 1.20, "k_rate": 0.24},
        {"name": "벤자민", "era": 3.78, "whip": 1.26, "k_rate": 0.25},
        {"name": "소형준", "era": 4.23, "whip": 1.38, "k_rate": 0.20},
        {"name": "웨스",   "era": 4.01, "whip": 1.32, "k_rate": 0.22},
        {"name": "김민",   "era": 4.56, "whip": 1.46, "k_rate": 0.18},
    ],
    "SSG": [
        {"name": "로에니스", "era": 3.23, "whip": 1.17, "k_rate": 0.27},
        {"name": "김광현",   "era": 3.56, "whip": 1.22, "k_rate": 0.25},
        {"name": "오원석",   "era": 4.12, "whip": 1.34, "k_rate": 0.21},
        {"name": "이태양",   "era": 4.45, "whip": 1.43, "k_rate": 0.19},
        {"name": "박종훈",   "era": 4.23, "whip": 1.37, "k_rate": 0.20},
    ],
    "Lotte": [
        {"name": "스트레일리", "era": 3.67, "whip": 1.24, "k_rate": 0.26},
        {"name": "박세웅",     "era": 4.12, "whip": 1.35, "k_rate": 0.22},
        {"name": "윤성빈",     "era": 4.56, "whip": 1.45, "k_rate": 0.19},
        {"name": "글라버",     "era": 3.89, "whip": 1.29, "k_rate": 0.24},
        {"name": "나균안",     "era": 4.78, "whip": 1.52, "k_rate": 0.17},
    ],
    "Hanwha": [
        {"name": "류현진", "era": 3.34, "whip": 1.19, "k_rate": 0.25},
        {"name": "문동주", "era": 4.01, "whip": 1.31, "k_rate": 0.23},
        {"name": "노경은", "era": 4.45, "whip": 1.43, "k_rate": 0.19},
        {"name": "샤이너", "era": 3.78, "whip": 1.26, "k_rate": 0.24},
        {"name": "김범수", "era": 4.89, "whip": 1.55, "k_rate": 0.17},
    ],
    "NC": [
        {"name": "카일",   "era": 3.45, "whip": 1.21, "k_rate": 0.26},
        {"name": "신민혁", "era": 4.12, "whip": 1.34, "k_rate": 0.21},
        {"name": "이재학", "era": 4.34, "whip": 1.40, "k_rate": 0.20},
        {"name": "루친스키", "era": 3.67, "whip": 1.24, "k_rate": 0.25},
        {"name": "박진우", "era": 4.67, "whip": 1.48, "k_rate": 0.18},
    ],
    "Kiwoom": [
        {"name": "하헤도",   "era": 3.56, "whip": 1.22, "k_rate": 0.25},
        {"name": "안우진",   "era": 3.89, "whip": 1.28, "k_rate": 0.24},
        {"name": "김선기",   "era": 4.34, "whip": 1.40, "k_rate": 0.20},
        {"name": "주승우",   "era": 4.67, "whip": 1.48, "k_rate": 0.18},
        {"name": "이병준",   "era": 4.89, "whip": 1.54, "k_rate": 0.17},
    ]
}


def get_team_stats(team: str) -> dict:
    """
    팀 스탯 반환
    :param team: 구단명 (예: "KIA")
    :return: 팀 스탯 딕셔너리
    """
    return TEAM_STATS.get(team, {})


def get_pitchers(team: str) -> list:
    """
    구단별 선발투수 목록 반환
    :param team: 구단명
    :return: 투수 목록 리스트
    """
    return PITCHERS.get(team, [])


def get_pitcher_names(team: str) -> list:
    """
    구단별 선발투수 이름 목록 반환 (드롭다운용)
    :param team: 구단명
    :return: 투수 이름 리스트
    """
    return [p["name"] for p in PITCHERS.get(team, [])]


def get_pitcher_stats(team: str, name: str) -> dict:
    """
    특정 투수 스탯 반환
    :param team: 구단명
    :param name: 투수 이름
    :return: 투수 스탯 딕셔너리
    """
    pitchers = PITCHERS.get(team, [])
    for p in pitchers:
        if p["name"] == name:
            return p
    return {}
