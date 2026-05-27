"""
투표 관리 모듈
- 닉네임 기반 투표 저장/조회
- JSON 파일로 데이터 관리
"""

import json
import os
from datetime import datetime

# 투표 데이터 저장 경로
VOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../votes.json")


def _load_votes() -> dict:
    """votes.json 파일 로드"""
    try:
        if os.path.exists(VOTES_FILE):
            with open(VOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_votes(data: dict) -> None:
    """votes.json 파일 저장"""
    try:
        with open(VOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"투표 저장 오류: {e}")


def get_today_key() -> str:
    """오늘 날짜 키 반환 (예: 2026-05-26)"""
    return datetime.now().strftime("%Y-%m-%d")


def get_match_key(away: str, home: str) -> str:
    """경기 키 반환 (예: KIA vs 키움)"""
    return f"{away} vs {home}"


def submit_vote(nickname: str, match_key: str, pick: str) -> dict:
    """
    투표 제출
    :param nickname: 닉네임
    :param match_key: 경기 키 (예: "KIA vs 키움")
    :param pick: 선택한 팀
    :return: {"success": True/False, "message": "메시지"}
    """
    if not nickname or not nickname.strip():
        return {"success": False, "message": "닉네임을 입력해주세요!"}

    nickname = nickname.strip()
    today = get_today_key()
    data = _load_votes()

    # 날짜 초기화
    if today not in data:
        data[today] = {}

    # 경기 초기화
    if match_key not in data[today]:
        data[today][match_key] = {"votes": {}, "counts": {}}

    match_data = data[today][match_key]

    # 중복 투표 확인
    if nickname in match_data["votes"]:
        prev_pick = match_data["votes"][nickname]
        if prev_pick == pick:
            return {"success": False, "message": f"이미 {pick}에 투표하셨습니다!"}
        else:
            # 이전 투표 취소 후 새로 투표
            match_data["counts"][prev_pick] = match_data["counts"].get(prev_pick, 1) - 1

    # 투표 저장
    match_data["votes"][nickname] = pick
    match_data["counts"][pick] = match_data["counts"].get(pick, 0) + 1

    _save_votes(data)
    return {"success": True, "message": f"{pick} 투표 완료!"}


def get_vote_counts(match_key: str) -> dict:
    """
    경기별 투표 현황 반환
    :param match_key: 경기 키
    :return: {"팀A": 72, "팀B": 28, "total": 100}
    """
    today = get_today_key()
    data = _load_votes()

    if today not in data or match_key not in data[today]:
        return {"total": 0}

    counts = data[today][match_key].get("counts", {})
    total = sum(counts.values())
    counts["total"] = total
    return counts


def get_vote_percentage(match_key: str, away: str, home: str) -> dict:
    """
    투표 비율 반환
    :return: {"away_pct": 65, "home_pct": 35, "total": 100}
    """
    counts = get_vote_counts(match_key)
    total = counts.get("total", 0)

    if total == 0:
        return {"away_pct": 50, "home_pct": 50, "total": 0}

    away_count = counts.get(away, 0)
    home_count = counts.get(home, 0)
    away_pct = round(away_count / total * 100)
    home_pct = 100 - away_pct

    return {
        "away_pct": away_pct,
        "home_pct": home_pct,
        "away_count": away_count,
        "home_count": home_count,
        "total": total
    }


def has_voted(nickname: str, match_key: str) -> str | None:
    """
    닉네임의 투표 여부 확인
    :return: 투표한 팀 이름 or None
    """
    if not nickname:
        return None

    today = get_today_key()
    data = _load_votes()

    if today not in data or match_key not in data[today]:
        return None

    return data[today][match_key]["votes"].get(nickname.strip())


def get_all_today_votes() -> dict:
    """오늘 전체 투표 현황 반환"""
    today = get_today_key()
    data = _load_votes()
    return data.get(today, {})
