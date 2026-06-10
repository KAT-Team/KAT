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

def get_all_results(start_date: str = "2026-03-28") -> list:
    """
    시즌 시작부터 오늘까지 전체 경기 결과 반환 (월별로 나눠서 요청)
    """
    from datetime import timedelta

    all_results = []
    end_date = datetime.now().strftime("%Y-%m-%d")
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while current <= end:
        # 해당 월의 마지막 날 계산
        if current.month == 12:
            month_end = current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current.replace(month=current.month+1, day=1) - timedelta(days=1)

        to_date = min(month_end, end).strftime("%Y-%m-%d")
        from_date = current.strftime("%Y-%m-%d")

        url = f"https://api-gw.sports.naver.com/schedule/games?fields=basic%2Cschedule%2Cbaseball%2CmanualRelayUrl&upperCategoryId=kbaseball&fromDate={from_date}&toDate={to_date}&size=500"

        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            games = res.json().get("result", {}).get("games", [])

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

                all_results.append({
                    "date": game.get("gameDate", ""),
                    "home": home_eng,
                    "away": away_eng,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status,
                    "winner": winner,
                    "stadium": game.get("stadium", ""),
                    "game_id": game.get("gameId", ""),
                    "cancel": game.get("cancel", False),
                    "suspended": game.get("suspended", False)
                })

        except Exception as e:
            print(f"경기 결과 크롤링 오류 ({from_date}): {e}")

        current = month_end + timedelta(days=1)

    return all_results



if __name__ == "__main__":
    results = get_today_results()
    for r in results:
        print(r)
