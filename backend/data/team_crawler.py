"""
KBO 팀 스탯 크롤링 모듈
- 팀 순위, 승률, 최근 경기
- 팀 타율 (AVG)
- 팀 ERA
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# 한글 팀명 → 영어 코드 변환
TEAM_NAME_KR = {
    "기아": "KIA",
    "삼성": "Samsung",
    "LG": "LG",
    "두산": "Doosan",
    "KT": "KT",
    "SSG": "SSG",
    "롯데": "Lotte",
    "한화": "Hanwha",
    "NC": "NC",
    "키움": "Kiwoom"
}


def crawl_team_ranking() -> dict:
    """
    팀 순위, 승률, 최근 경기 크롤링
    """
    url = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        table = None
        for t in soup.find_all("table"):
            summary = t.get("summary", "")
            if summary and "순위" in summary:
                table = t
                break

        if not table:
            return {}

        ranking = {}
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            rank = int(cols[0].text.strip())
            team_kr = cols[1].text.strip()
            win = int(cols[3].text.strip())
            lose = int(cols[4].text.strip())
            draw = int(cols[5].text.strip())
            win_rate = float(cols[6].text.strip())
            recent_10 = cols[8].text.strip()
            streak = cols[9].text.strip()
            home_record = cols[10].text.strip()    # 추가: 홈 기록 예) "20승5패"
            away_record = cols[11].text.strip()    # 추가: 원정 기록
            home_win_rate = _parse_win_rate(home_record)
            away_win_rate = _parse_win_rate(away_record)
            team_eng = TEAM_NAME_KR.get(team_kr, team_kr)
            recent_5 = _parse_recent_results(recent_10)

            ranking[team_eng] = {
                "rank": rank,
                "team_kr": team_kr,
                "win": win,
                "lose": lose,
                "draw": draw,
                "win_rate": win_rate,
                "recent_10": recent_10,
                "recent_5": recent_5,
                "streak": streak,
                "home_record": home_record,      # 추가
                "away_record": away_record,      # 추가
                "home_win_rate": home_win_rate,  # 추가
                "away_win_rate": away_win_rate,  # 추가
            }

        return ranking

    except Exception as e:
        print(f"팀 순위 크롤링 오류: {e}")
        return {}

def _parse_win_rate(record: str) -> float:
    """
    "20승5패2무" 형태 문자열에서 승률 계산
    """
    try:
        parts = record.split("-")
        w = int(parts[0])
        d = int(parts[1])
        l = int(parts[2])
        total = w + l
        return round(w / total, 3) if total > 0 else 0.5
    except:
        return 0.5

def crawl_team_batting() -> dict:
    """
    팀 타율 크롤링
    :return: {"KIA": {"avg": 0.267, "hr": 59}, ...}
    """
    url = "https://www.koreabaseball.com/Record/Team/Hitter/BasicOld.aspx"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table", {"class": "tData"})
        if not table:
            return {}

        batting = {}
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 16:
                continue

            team_kr = cols[1].text.strip()
            avg = float(cols[2].text.strip())
            ab = int(cols[4].text.strip())
            runs = int(cols[5].text.strip())
            hits = int(cols[6].text.strip())
            hr = int(cols[9].text.strip())
            tb = int(cols[10].text.strip())
            team_rbi = int(cols[11].text.strip())
            bb = int(cols[14].text.strip())
            hbp = int(cols[15].text.strip())
            team_eng = TEAM_NAME_KR.get(team_kr, team_kr)

            # OBP = (H + BB + HBP) / (AB + BB + HBP)
            obp = (hits + bb + hbp) / (ab + bb + hbp) if (ab + bb + hbp) > 0 else 0
            # SLG = TB / AB
            slg = tb / ab if ab > 0 else 0
            # OPS = OBP + SLG
            ops = round(obp + slg, 3)


            batting[team_eng] = {
                "avg": avg,
                "hr": hr,
                "runs": runs,
                "ops": ops,
                "team_rbi": team_rbi,
                "avg_display": f".{str(avg).split('.')[1][:3]}" if '.' in str(avg) else str(avg)
            }

        return batting

    except Exception as e:
        print(f"팀 타율 크롤링 오류: {e}")
        return {}


def crawl_team_pitching() -> dict:
    """
    팀 ERA 크롤링
    :return: {"KIA": {"era": 4.20}, ...}
    """
    url = "https://www.koreabaseball.com/Record/Team/Pitcher/BasicOld.aspx"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table", {"class": "tData"})
        if not table:
            return {}

        pitching = {}
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 19:
                continue

            team_kr = cols[1].text.strip()
            era = float(cols[2].text.strip())
            runs_allowed = int(cols[18].text.strip())
            team_eng = TEAM_NAME_KR.get(team_kr, team_kr)

            pitching[team_eng] = {
                "era": era,
                "era_display": str(era),
                "team_r": team_r
                "runs_allowed": runs_allowed
            }

        return pitching

    except Exception as e:
        print(f"팀 ERA 크롤링 오류: {e}")
        return {}


def crawl_all_team_stats() -> dict:
    """
    팀 전체 스탯 통합 크롤링
    순위 + 타율 + ERA 합산
    :return: {
        "KIA": {
            "rank": 4,
            "win_rate": 0.542,
            "avg": 0.267,
            "avg_display": ".267",
            "era": 4.20,
            "era_display": "4.20",
            "recent_5": [...],
            "recent_10": "8승0무2패",
            "streak": "4승"
        }, ...
    }
    """
    print("팀 순위 크롤링 중...")
    ranking = crawl_team_ranking()

    print("팀 타율 크롤링 중...")
    batting = crawl_team_batting()

    print("팀 ERA 크롤링 중...")
    pitching = crawl_team_pitching()

    # 통합
    result = {}
    all_teams = set(list(ranking.keys()) + list(batting.keys()) + list(pitching.keys()))

    for team in all_teams:
        result[team] = {}
        if team in ranking:
            result[team].update(ranking[team])
        if team in batting:
            result[team].update(batting[team])
        if team in pitching:
            result[team].update(pitching[team])

    return result


def _parse_recent_results(recent_10: str) -> list:
    """
    최근 10경기 문자열에서 최근 5경기 결과 리스트 추출
    """
    try:
        import re
        win_match = re.search(r"(\d+)승", recent_10)
        draw_match = re.search(r"(\d+)무", recent_10)
        lose_match = re.search(r"(\d+)패", recent_10)

        wins = int(win_match.group(1)) if win_match else 0
        draws = int(draw_match.group(1)) if draw_match else 0
        loses = int(lose_match.group(1)) if lose_match else 0

        total = wins + draws + loses
        if total == 0:
            return []

        results = []
        remaining_w = wins
        remaining_d = draws
        remaining_l = loses

        for i in range(5):
            remaining = total - i
            if remaining <= 0:
                break
            if remaining_w / remaining >= 0.5:
                results.append("승")
                remaining_w -= 1
            elif remaining_l / remaining >= 0.5:
                results.append("패")
                remaining_l -= 1
            else:
                results.append("무")
                remaining_d -= 1

        return results
    except:
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("KBO 팀 전체 스탯 크롤링 테스트")
    print("=" * 60)

    stats = crawl_all_team_stats()

    print("\n결과:")
    for team, data in stats.items():
        print(
            f"{data.get('rank', '-')}위 {team}({data.get('team_kr', '')}) | "
            f"승률 {data.get('win_rate', '-')} | "
            f"타율 {data.get('avg_display', '-')} | "
            f"ERA {data.get('era_display', '-')} | "
            f"최근5경기 {data.get('recent_5', [])}"
        )
