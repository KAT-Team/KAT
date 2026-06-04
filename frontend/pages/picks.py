"""
승부예측 페이지
- 선발 투수 성적
- 팀 성적 (타율, ERA 등)
- 팀 최근 경기 전적
- 배당률 정보
"""

import streamlit as st
from backend.data.team_stats import get_team_stats, get_pitcher_names, get_pitcher_stats
from backend.simulation.predict import calc_win_probability

# ✅ 1. TEAM_NAME_KR 먼저 정의
TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG",
    "두산": "Doosan", "KT": "KT", "SSG": "SSG",
    "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

# ✅ 2. TODAYS_MATCHES 정의
TODAYS_MATCHES = [
    {
        "away": "KIA", "away_logo": "frontend/assets/logo_kia.svg", "away_pitcher": "김태형",
        "away_team_avg": ".268", "away_team_era": "4.25", "away_rank": "#4",
        "away_recent": ["승", "패", "승", "승", "승"],
        "home": "키움", "home_logo": "frontend/assets/logo_kiwoom.svg", "home_pitcher": "안우진",
        "home_team_avg": ".233", "home_team_era": "4.99", "home_rank": "#9",
        "home_recent": ["승", "승", "승", "패", "패"]
    },
    {
        "away": "LG", "away_logo": "frontend/assets/logo_lg.svg", "away_pitcher": "톨허스트",
        "away_team_avg": ".264", "away_team_era": "4.34", "away_rank": "#2",
        "away_recent": ["패", "승", "패", "승", "승"],
        "home": "롯데", "home_logo": "frontend/assets/logo_lotte.svg", "home_pitcher": "비슬리",
        "home_team_avg": ".259", "home_team_era": "4.41", "home_rank": "#8",
        "home_recent": ["승", "승", "패", "승", "패"]
    },
    {
        "away": "삼성", "away_logo": "frontend/assets/logo_samsung.svg", "away_pitcher": "원태인",
        "away_team_avg": ".278", "away_team_era": "4.09", "away_rank": "#1",
        "away_recent": ["승", "승", "승", "패", "승"],
        "home": "SSG", "home_logo": "frontend/assets/logo_ssg.svg", "home_pitcher": "베니지아노",
        "home_team_avg": ".264", "home_team_era": "5.04", "home_rank": "#6",
        "home_recent": ["패", "패", "패", "패", "패"]
    },
    {
        "away": "한화", "away_logo": "frontend/assets/logo_hanwha.svg", "away_pitcher": "에르난데스",
        "away_team_avg": ".279", "away_team_era": "5.03", "away_rank": "#5",
        "away_recent": ["패", "패", "승", "승", "승"],
        "home": "NC", "home_logo": "frontend/assets/logo_nc.svg", "home_pitcher": "테일러",
        "home_team_avg": ".263", "home_team_era": "4.68", "home_rank": "#10",
        "home_recent": ["패", "패", "패", "패", "승"]
    },
    {
        "away": "KT", "away_logo": "frontend/assets/logo_kt.svg", "away_pitcher": "보쉴리",
        "away_team_avg": ".290", "away_team_era": "4.66", "away_rank": "#3",
        "away_recent": ["패", "패", "승", "승", "패"],
        "home": "두산", "home_logo": "frontend/assets/logo_doosan.svg", "home_pitcher": "최민석",
        "home_team_avg": ".258", "home_team_era": "4.04", "home_rank": "#6",
        "home_recent": ["승", "승", "패", "패", "패"]
    },
]

# ✅ 3. predict.py로 승률 자동 계산 (TEAM_NAME_KR, TODAYS_MATCHES 정의 후)
for match in TODAYS_MATCHES:
    away_team_eng = str(TEAM_NAME_KR.get(match["away"], match["away"]))
    home_team_eng = str(TEAM_NAME_KR.get(match["home"], match["home"]))

    result = calc_win_probability(
        home_team=home_team_eng,
        away_team=away_team_eng,
        home_pitcher=match["home_pitcher"],
        away_pitcher=match["away_pitcher"],
        home_condition=50,
        away_condition=50
    )
    match["away_pct"] = result["away_prob"]
    match["home_pct"] = result["home_prob"]


# 투표율 연동형 배당률 계산 함수
def calculate_odds(pct):
    if pct == 0:
        return 99.0
    odds = round(100 / pct, 2)
    return max(odds, 1.15)


def toggle_vote(match_idx, clicked_side):
    if clicked_side == "away":
        if st.session_state[f"chk_away_{match_idx}"]:
            st.session_state[f"chk_home_{match_idx}"] = False
    elif clicked_side == "home":
        if st.session_state[f"chk_home_{match_idx}"]:
            st.session_state[f"chk_away_{match_idx}"] = False


def show():
    # 1. 화면을 좌우 여백과 중앙 콘텐츠 영역으로 분할 (비율: 여백 1.5, 본문 7, 여백 1.5)
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    with center_content:
        if "user_points" not in st.session_state:
            st.session_state["user_points"] = 0

        st.markdown("### 🔮 승부 예측")
        st.markdown("<p style='font-size: 14px; color: gray;'>오늘의 경기 목록입니다. 전력을 비교해 보세요!</p>", unsafe_allow_html=True)
        base_reward_point = 100
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("#### 📅 [5/26] 오늘의 경기 라인업")

        selected_predictions = []

        for i, match in enumerate(TODAYS_MATCHES):
            with st.container(border=True):
                col_away, col_vs, col_home = st.columns([5, 2, 5])

                state_key = f"match_select_{i}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = "미선택"

                away_odds = calculate_odds(match['away_pct'])
                home_odds = calculate_odds(match['home_pct'])
                away_reward = int(base_reward_point * away_odds)
                home_reward = int(base_reward_point * home_odds)

                with col_away:
                    c_a1, c_a2, c_a3 = st.columns([1, 1, 10])
                    with c_a1:
                        st.checkbox("", key=f"chk_away_{i}", label_visibility="collapsed", on_change=toggle_vote, args=(i, "away"))
                    with c_a2:
                        st.image(match["away_logo"], width=35)
                    with c_a3:
                        away_w = match["away_recent"].count("승")
                        away_l = match["away_recent"].count("패")
                        st.markdown(
                            f"<div style='text-align: left; line-height: 1.3;'>"
                            f"<span style='font-size:11px; color:#718096; background-color:#EDF2F7; padding:1px 4px; border-radius:3px; margin-right:4px; vertical-align:middle;'>{match['away_rank']}</span>"
                            f"<b style='font-size:16px; vertical-align:middle;'>{match['away']} </b>"
                            f"<span style='background-color:#E2E8F0; font-size:11px; padding:2px 4px; border-radius:3px; color:#4A5568; vertical-align:middle;'> 원정</span><br>"
                            f"<span style='font-size:12px; color:#4A5568;'>{match['away_pitcher']}</span><br>"
                            f"<span style='font-size:11px; color:#718096; background-color:#F7FAFC; padding:2px 6px; border-radius:4px; border:1px solid #E2E8F0; white-space:nowrap;'>"
                            f"타율 {match['away_team_avg']} | ERA {match['away_team_era']} | 최근 5경기 : {away_w}W {away_l}L"
                            f"</span></div>",
                            unsafe_allow_html=True
                        )

                with col_vs:
                    st.markdown(
                        f"<div style='display: flex; justify-content: space-between; font-size: 12px; color: #4A5568; font-weight: bold; margin-bottom: -3px;'>"
                        f"<span>{match['away_pct']}%</span>"
                        f"<span>{match['home_pct']}%</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.progress(match['away_pct'] / 100)
                    st.markdown(
                        f"<div style='display: flex; justify-content: space-between; font-size: 11px; font-weight: bold; margin-top: 2px;'>"
                        f"<span style='color:#ff4b4b;'>+{away_reward:,}P</span>"
                        f"<span style='color:#ff4b4b;'>+{home_reward:,}P</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown("<p style='text-align: center; font-size: 10px; color: #A0AEC0; margin-top: -3px; margin-bottom: 0;'>성적 기반 승률 예측 / 리워드</p>", unsafe_allow_html=True)

                with col_home:
                    c_h3, c_h2, c_h1 = st.columns([10, 1, 1])
                    with c_h3:
                        home_w = match["home_recent"].count("승")
                        home_l = match["home_recent"].count("패")
                        st.markdown(
                            f"<div style='text-align: right; line-height: 1.3;'>"
                            f"<span style='font-size:11px; color:#718096; background-color:#EDF2F7; padding:1px 4px; border-radius:3px; margin-right:4px; vertical-align:middle;'>{match['home_rank']}</span>"
                            f"<b style='font-size:16px; vertical-align:middle;'>{match['home']}</b> "
                            f"<span style='background-color:#E2E8F0; font-size:11px; padding:2px 4px; border-radius:3px; color:#4A5568; vertical-align:middle;'>홈</span><br>"
                            f"<span style='font-size:12px; color:#4A5568;'>{match['home_pitcher']}</span><br>"
                            f"<span style='font-size:11px; color:#718096; background-color:#F7FAFC; padding:2px 6px; border-radius:4px; border:1px solid #E2E8F0; white-space:nowrap;'>"
                            f"타율 {match['home_team_avg']} | ERA {match['home_team_era']} | 최근 5경기 : {home_w}W {home_l}L"
                            f"</span></div>",
                            unsafe_allow_html=True
                        )
                    with c_h2:
                        st.image(match["home_logo"], width=35)
                    with c_h1:
                        st.checkbox("", key=f"chk_home_{i}", label_visibility="collapsed", on_change=toggle_vote, args=(i, "home"))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("승부예측 제출하기", type="primary", use_container_width=True):
            error_message = None
            selected_predictions = []
            total_potential_reward = 0

            for i, match in enumerate(TODAYS_MATCHES):
                match_name = f"{match['away']} vs {match['home']}"
                away_selected = st.session_state.get(f"chk_away_{i}", False)
                home_selected = st.session_state.get(f"chk_home_{i}", False)

                away_odds = calculate_odds(match['away_pct'])
                home_odds = calculate_odds(match['home_pct'])

                if not away_selected and not home_selected:
                    error_message = f"⚠️ [{match_name}] 경기의 예측이 누락되었습니다."
                    break

                if away_selected:
                    reward = int(base_reward_point * away_odds)
                    total_potential_reward += reward
                    selected_predictions.append(f"🟢 {match['away']} 승리 선택 ➡️ 적중 시 {reward:,} P 지급")
                elif home_selected:
                    reward = int(base_reward_point * home_odds)
                    total_potential_reward += reward
                    selected_predictions.append(f"🟢 {match['home']} 승리 선택 ➡️ 적중 시 {reward:,} P 지급")

            if error_message:
                st.error(error_message)
            else:
                st.success("🎉 오늘의 승부예측 투표가 모두 접수되었습니다! 경기 종료 후 포인트를 확인하세요.")
                st.markdown("### 📑 투표 접수 확인서")
                st.markdown(f"- **현재 나의 포인트:** `💰 {st.session_state['user_points']:,} P`")
                st.markdown(f"- **모든 경기 적중 시 최대 보상:** `🔥 +{total_potential_reward:,} P`")
                st.divider()
                for pred in selected_predictions:
                    st.caption(pred)
