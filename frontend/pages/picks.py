"""
승부예측 페이지
- kbo_schedule.json 기반 오늘의 경기 스케줄 동적 로드
- 구단별 팀 타율 및 ERA 데이터 매핑 레이어 추가
"""

import os
import json
from datetime import datetime
import streamlit as st

# 1️⃣ 구단 명칭 변환 및 이미지 매핑을 위한 사전
TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG",
    "두산": "Doosan", "KT": "KT", "SSG": "SSG",
    "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

# 2️⃣ [신규] 팀별 성적 데이터베이스 (추후 백엔드 크롤링 데이터와 연동되는 지점)
# 임의의 값이 아닌, 직관적인 비교를 위해 팀별 기본 성적 수치를 사전으로 관리합니다.
TEAM_STATS = {
    "기아": {"avg": ".291", "era": "3.95"},
    "삼성": {"avg": ".268", "era": "4.21"},
    "LG": {"avg": ".282", "era": "4.10"},
    "두산": {"avg": ".275", "era": "4.45"},
    "KT": {"avg": ".270", "era": "4.62"},
    "SSG": {"avg": ".273", "era": "4.85"},
    "롯데": {"avg": ".265", "era": "4.90"},
    "한화": {"avg": ".261", "era": "4.55"},
    "NC": {"avg": ".271", "era": "4.30"},
    "키움": {"avg": ".258", "era": "5.12"}
}


def load_todays_matches_from_json():
    now = datetime.now()

    # 요일 한글 변환
    weeks = ["월", "화", "수", "목", "금", "토", "일"]
    week_kr = weeks[now.weekday()]

    # 크롤러가 생성하는 포맷과 완벽 싱크 매칭: "5월 05.01(금)"
    match_date_str = f"{now.month}월 {now.month:02d}.{now.day:02d}({week_kr})"

    # 💡 [테스트 팁] 오늘 경기가 없는 날이라면 아래 주석을 풀고 json에 있는 날짜로 테스트하세요!
    # match_date_str = "5월 05.01(금)"

    json_path = os.path.join("backend", "data", "kbo_schedule.json")

    if not os.path.exists(json_path):
        # 만약 크롤러가 루트에 저장했다면 찾을 수 있도록 예외 대안 경로 설정
        if os.path.exists("kbo_schedule.json"):
            json_path = "kbo_schedule.json"
        else:
            st.error(f"🚨 스케줄 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_path}")
            return []

    with open(json_path, "r", encoding="utf-8") as f:
        all_schedules = json.load(f)

    todays_raw_matches = [m for m in all_schedules if m.get("날짜") == match_date_str]

    todays_matches = []
    for match in todays_raw_matches:
        teams = match["경기"].split(" vs ")
        if len(teams) != 2:
            continue

        away_team = teams[0].strip()
        home_team = teams[1].strip()

        away_eng = TEAM_NAME_KR.get(away_team, "kia").lower()
        home_eng = TEAM_NAME_KR.get(home_team, "kiwoom").lower()

        # [핵심] TEAM_STATS 사전에서 해당 팀의 성적 쏙 빼오기 (없으면 기본값 처리하여 팅김 방지)
        away_stat = TEAM_STATS.get(away_team, {"avg": ".000", "era": "0.00"})
        home_stat = TEAM_STATS.get(home_team, {"avg": ".000", "era": "0.00"})

        todays_matches.append({
            "away": away_team,
            "away_logo": f"frontend/assets/logo_{away_eng}.svg",
            "away_avg": away_stat["avg"],
            "away_era": away_stat["era"],

            "home": home_team,
            "home_logo": f"frontend/assets/logo_{home_eng}.svg",
            "home_avg": home_stat["avg"],
            "home_era": home_stat["era"],

            "time": match.get("시간", "18:30"),
            "stadium": match.get("구장", "야구장")
        })

    return todays_matches


# 데이터 로드
TODAYS_MATCHES = load_todays_matches_from_json()


def toggle_vote(match_idx, clicked_side):
    if clicked_side == "away":
        if st.session_state[f"chk_away_{match_idx}"]:
            st.session_state[f"chk_home_{match_idx}"] = False
    elif clicked_side == "home":
        if st.session_state[f"chk_home_{match_idx}"]:
            st.session_state[f"chk_away_{match_idx}"] = False


def show():
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    with center_content:
        st.markdown("### 🔮 승부 예측")
        st.markdown("<p style='font-size: 14px; color: gray;'>오늘의 경기 스케줄과 팀 전력 정보입니다.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        now = datetime.now()
        st.markdown(f"#### 📅 [{now.month}/{now.day}] 오늘의 경기 라인업")

        if not TODAYS_MATCHES:
            st.info("오늘 예정된 KBO 경기 일정이 없거나, 날짜가 매칭되지 않습니다.")
            return

        for i, match in enumerate(TODAYS_MATCHES):
            with st.container(border=True):
                col_away, col_vs, col_home = st.columns([5, 2, 5])

                # 1. 원정 팀 영역 (왼쪽)
                with col_away:
                    c_a1, c_a2, c_a3 = st.columns([1, 2, 9])
                    with c_a1:
                        st.checkbox("", key=f"chk_away_{i}", label_visibility="collapsed", on_change=toggle_vote, args=(i, "away"))
                    with c_a2:
                        if os.path.exists(match["away_logo"]):
                            st.image(match["away_logo"], width=35)
                        else:
                            st.text("⚾")
                    with c_a3:
                        st.markdown(
                            f"<div style='line-height:1.4; text-align:left;'>"
                            f"<b>{match['away']}</b> <span style='color:gray; font-size:11px;'>원정</span><br>"
                            f"<span style='font-size:11px; color:#4A5568; background-color:#F7FAFC; padding:1px 4px; border:1px solid #E2E8F0; border-radius:3px;'>"
                            f"팀타율 {match['away_avg']} | ERA {match['away_era']}"
                            f"</span></div>",
                            unsafe_allow_html=True
                        )

                # 2. 가운데 영역 (시간 및 구장)
                with col_vs:
                    st.markdown(f"<div style='text-align:center; font-weight:bold; font-size:15px; margin-top:2px; color:#2D3748;'>{match['time']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; color:#718096; font-size:11px; margin-top:2px;'>📍 {match['stadium']}</div>", unsafe_allow_html=True)

                # 3. 홈 팀 영역 (오른쪽)
                with col_home:
                    c_h3, c_h2, c_h1 = st.columns([9, 2, 1])
                    with c_h3:
                        st.markdown(
                            f"<div style='line-height:1.4; text-align:right;'> "
                            f"<span style='color:gray; font-size:11px;'>홈</span> <b>{match['home']}</b><br>"
                            f"<span style='font-size:11px; color:#4A5568; background-color:#F7FAFC; padding:1px 4px; border:1px solid #E2E8F0; border-radius:3px;'>"
                            f"팀타율 {match['home_avg']} | ERA {match['home_era']}"
                            f"</span></div>",
                            unsafe_allow_html=True
                        )
                    with c_h2:
                        if os.path.exists(match["home_logo"]):
                            st.image(match["home_logo"], width=35)
                        else:
                            st.text("⚾")
                    with c_h1:
                        st.checkbox("", key=f"chk_home_{i}", label_visibility="collapsed", on_change=toggle_vote, args=(i, "home"))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("승부예측 제출하기", type="primary", use_container_width=True):
            st.success("🎉 투표가 접수되었습니다!")
