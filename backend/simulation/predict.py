"""
승리 확률 예측 시뮬레이션 모듈
- 팀 승률 + 투수 스탯 + 컨디션 변수 기반 순수 통계 계산
- AI/ML 모델 미사용
"""

from backend.data.team_stats import get_team_stats, get_pitcher_stats


def calc_win_probability(
    home_team: str,
    away_team: str,
    home_pitcher: str,
    away_pitcher: str,
    home_condition: int,
    away_condition: int
) -> dict:
    """
    승리 확률 계산 메인 함수
    :param home_team: 홈팀 구단명 (예: "KIA")
    :param away_team: 원정팀 구단명 (예: "LG")
    :param home_pitcher: 홈팀 선발투수 이름
    :param away_pitcher: 원정팀 선발투수 이름
    :param home_condition: 홈팀 투수 컨디션 (0~100)
    :param away_condition: 원정팀 투수 컨디션 (0~100)
    :return: {
        "home_prob": 57,
        "away_prob": 43,
        "comment": "분석 코멘트",
        "factors": { 세부 요인 }
    }
    """
    home_stats = get_team_stats(home_team)
    away_stats = get_team_stats(away_team)
    home_pitcher_stats = get_pitcher_stats(home_team, home_pitcher)
    away_pitcher_stats = get_pitcher_stats(away_team, away_pitcher)

    if not home_stats or not away_stats:
        return {"home_prob": 50, "away_prob": 50, "comment": "데이터 없음", "factors": {}}

    # 1. 기본 승률 기반 확률
    home_wr = home_stats.get("win_rate", 0.5)
    away_wr = away_stats.get("win_rate", 0.5)
    base_prob = home_wr / (home_wr + away_wr)

    # 2. 홈 어드밴티지 보정 (+3%)
    home_advantage = 0.03

    # 3. 컨디션 보정
    # 50점 = 보정 없음, 100점 = +10%, 0점 = -10%
    home_condition_bonus = (home_condition - 50) * 0.002
    away_condition_bonus = (away_condition - 50) * 0.002

    # 4. 투수 ERA 보정
    # ERA가 낮을수록 유리 (평균 ERA 4.00 기준)
    home_era = home_pitcher_stats.get("era", 4.00) if home_pitcher_stats else 4.00
    away_era = away_pitcher_stats.get("era", 4.00) if away_pitcher_stats else 4.00
    era_bonus = (away_era - home_era) * 0.01

    # 5. 최종 확률 계산
    home_prob = base_prob + home_advantage + home_condition_bonus - away_condition_bonus + era_bonus
    home_prob = max(0.1, min(0.9, home_prob))  # 10~90% 범위 제한
    away_prob = 1 - home_prob

    # 6. 분석 코멘트 생성
    comment = _generate_comment(
        home_team, away_team,
        home_prob, away_prob,
        home_condition, away_condition,
        home_era, away_era,
        home_wr, away_wr
    )

    return {
        "home_prob": round(home_prob * 100),
        "away_prob": round(away_prob * 100),
        "comment": comment,
        "factors": {
            "base_prob": round(base_prob * 100, 1),
            "home_advantage": round(home_advantage * 100, 1),
            "home_condition_bonus": round(home_condition_bonus * 100, 1),
            "away_condition_bonus": round(away_condition_bonus * 100, 1),
            "era_bonus": round(era_bonus * 100, 1),
            "home_era": home_era,
            "away_era": away_era,
        }
    }


def _generate_comment(
    home_team: str,
    away_team: str,
    home_prob: float,
    away_prob: float,
    home_condition: int,
    away_condition: int,
    home_era: float,
    away_era: float,
    home_wr: float,
    away_wr: float
) -> str:
    """
    시뮬레이션 결과 분석 코멘트 자동 생성
    """
    condition_diff = home_condition - away_condition
    era_diff = away_era - home_era
    wr_diff = abs(home_wr - away_wr)

    # 우세한 팀
    leading_team = home_team if home_prob > away_prob else away_team
    leading_prob = max(home_prob, away_prob)

    # 코멘트 조합
    parts = []

    # 승률 차이
    if wr_diff >= 0.08:
        parts.append(f"기본 전력 차이에서 {leading_team}이 우위를 점하고 있습니다")
    elif wr_diff <= 0.02:
        parts.append("두 팀의 기본 전력은 거의 대등합니다")
    else:
        parts.append(f"시즌 전적상 {leading_team}이 소폭 앞서 있습니다")

    # 컨디션 차이
    if condition_diff >= 30:
        parts.append(f"홈팀 선발투수의 컨디션이 훨씬 좋아 홈팀에게 유리한 상황입니다")
    elif condition_diff <= -30:
        parts.append(f"원정팀 선발투수의 컨디션이 훨씬 좋아 원정팀이 유리합니다")
    elif abs(condition_diff) <= 10:
        parts.append("양 팀 선발투수 컨디션은 비슷한 수준입니다")
    else:
        better = "홈팀" if condition_diff > 0 else "원정팀"
        parts.append(f"{better} 선발투수 컨디션이 다소 앞서 있습니다")

    # ERA 차이
    if era_diff >= 0.5:
        parts.append(f"홈팀 선발투수의 ERA가 낮아 투수전에서 유리합니다")
    elif era_diff <= -0.5:
        parts.append(f"원정팀 선발투수의 ERA가 낮아 투수전이 기대됩니다")

    # 최종 예측
    if leading_prob >= 0.65:
        parts.append(f"종합적으로 {leading_team}의 우세가 뚜렷합니다")
    elif leading_prob >= 0.55:
        parts.append(f"종합적으로 {leading_team}이 약간 유리한 상황입니다")
    else:
        parts.append("두 팀이 매우 팽팽한 경기가 예상됩니다")

    return ". ".join(parts) + "!"
