"""
네이버 스포츠 API로 KBO 당일 경기 결과 가져오기
"""

import requests
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}

NAVER_TEAM_CODE = {
    "KIA": "KIA", "HT": "KIA",  # HT 추가
    "SS": "Samsung", "LG": "LG",
    "OB": "Doosan", "KT": "KT", "SK": "SSG",
    "LT": "Lotte", "HH": "Hanwha",
    "NC": "NC", "WO": "Kiwoom"
}

def get_today_results() -> list:
    """
    당일 KBO 경기 결과 반환
    :return: [
        {
            "home": "LG", "away": "SSG",
            "home_score": 5, "away_score": 3,
            "status": "RESULT",  # RESULT=종료, LIVE=진행중, SCHEDULED=예정
            "winner": "home"  # home / away / DRAW
        }, ...
    ]
    """
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api-gw.sports.naver.com/schedule/games?fields=basic%2Cschedule%2Cbaseball%2CmanualRelayUrl&upperCategoryId=kbaseball&fromDate={today}&toDate={today}&size=500"

    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        data = res.json()
        games = data.get("result", {}).get("games", [])

        results = []
        for game in games:
            if game.get("categoryId") != "kbo":
                continue

            home_code = game.get("homeTeamCode", "")
            away_code = game.get("awayTeamCode", "")
            home_eng = NAVER_TEAM_CODE.get(home_code, home_code)
            away_eng = NAVER_TEAM_CODE.get(away_code, away_code)
            home_score = game.get("homeTeamScore", 0)
            away_score = game.get("awayTeamScore", 0)
            status = game.get("statusCode", "")
            raw_winner = game.get("winner", "")

            if raw_winner == "HOME":
                winner = "home"
            elif raw_winner == "AWAY":
                winner = "away"
            else:
                winner = "draw"

            results.append({
                "home": home_eng,
                "away": away_eng,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "winner": winner,
                "stadium": game.get("stadium", ""),
                "game_id": game.get("gameId", "")
            })

        return results

    except Exception as e:
        print(f"네이버 경기 결과 크롤링 오류: {e}")
        return []


if __name__ == "__main__":
    results = get_today_results()
    for r in results:
        print(r)
