"""
승부예측 페이지
- 선발 투수 성적
- 팀 성적 (타율, ERA 등)
- 팀 최근 경기 전적
- 배당률 정보

- TODO : kbo_schedule.json 파일을 이용하여 TODAYS_MATCHES 수정
"""

import streamlit as st

TODAYS_MATCHES = [
    {
        "away": "KIA", "away_logo": "frontend/assets/logo_kia.svg", "away_pitcher": "김태형", "away_pct": 67,
        "away_team_avg": ".268", "away_team_era": "4.25", "away_rank": "#4",
        "away_recent": ["승", "패", "승", "승", "승"],
        "home": "키움", "home_logo": "frontend/assets/logo_kiwoom.svg", "home_pitcher": "안우진", "home_pct": 33,
        "home_team_avg": ".233", "home_team_era": "4.99", "home_rank": "#9",
        "home_recent": ["승", "승", "승", "패", "패"]
    },
    {
        "away": "LG", "away_logo": "frontend/assets/logo_lg.svg", "away_pitcher": "톨허스트", "away_pct": 64,
        "away_team_avg": ".264", "away_team_era": "4.34", "away_rank": "#2",
        "away_recent": ["패", "승", "패", "승", "승"],
        "home": "롯데", "home_logo": "frontend/assets/logo_lotte.svg", "home_pitcher": "비슬리", "home_pct": 36,
        "home_team_avg": ".259", "home_team_era": "4.41", "home_rank": "#8",
        "home_recent": ["승", "승", "패", "승", "패"]
    },
    {
        "away": "삼성", "away_logo": "frontend/assets/logo_samsung.svg", "away_pitcher": "원태인", "away_pct": 76,
        "away_team_avg": ".278", "away_team_era": "4.09", "away_rank": "#1",
        "away_recent": ["승", "승", "승", "패", "승"],
        "home": "SSG", "home_logo": "frontend/assets/logo_ssg.svg", "home_pitcher": "베니지아노", "home_pct": 24,
        "home_team_avg": ".264", "home_team_era": "5.04", "home_rank": "#6",
        "home_recent": ["패", "패", "패", "패", "패"]
    },
    {
        "away": "한화", "away_logo": "frontend/assets/logo_hanwha.svg", "away_pitcher": "에르난데스", "away_pct": 77,
        "away_team_avg": ".279", "away_team_era": "5.03", "away_rank": "#5",
        "away_recent": ["패", "패", "승", "승", "승"],
        "home": "NC", "home_logo": "frontend/assets/logo_nc.svg", "home_pitcher": "테일러", "home_pct": 23,
        "home_team_avg": ".263", "home_team_era": "4.68", "home_rank": "#10",
        "home_recent": ["패", "패", "패", "패", "승"]
    },
    {
        "away": "KT", "away_logo": "frontend/assets/logo_kt.svg", "away_pitcher": "보쉴리", "away_pct": 55,
        "away_team_avg": ".290", "away_team_era": "4.66", "away_rank": "#3",
        "away_recent": ["패", "패", "승", "승", "패"],
        "home": "두산", "home_logo": "frontend/assets/logo_doosan.svg", "home_pitcher": "최민석", "home_pct": 45,
        "home_team_avg": ".258", "home_team_era": "4.04", "home_rank": "#6",
        "home_recent": ["승", "승", "패", "패", "패"]
    },
]

# [추가] 투표율 연동형 배당률 계산 함수 (소수점 둘째 자리까지)
# 공식: 100 / 투표율 (최소 배당률 1.15로 방어)
def calculate_odds(pct):
    if pct == 0: return 99.0
    odds = round(100 / pct, 2)
    return max(odds, 1.15)

def toggle_vote(match_idx, clicked_side):
    if clicked_side == "away":
        # 원정을 켰을 때, 홈이 켜져 있다면 홈을 꺼버림
        if st.session_state[f"chk_away_{match_idx}"]:
            st.session_state[f"chk_home_{match_idx}"] = False
    elif clicked_side == "home":
        # 홈을 켰을 때, 원정이 켜져 있다면 원정을 꺼버림
        if st.session_state[f"chk_home_{match_idx}"]:
            st.session_state[f"chk_away_{match_idx}"] = False

def show():
    if "user_points" not in st.session_state:
        st.session_state["user_points"] = 0

    st.markdown("### 🔮 승부 예측")
    st.markdown("<p style='font-size: 14px; color: gray;'>오늘의 경기 목록입니다. 전력을 비교해 보세요!</p>", unsafe_allow_html=True)
    base_reward_point = 100
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### 📅 [5/26] 오늘의 경기 라인업")

    match_votes = []
    selected_predictions = []

    for i, match in enumerate(TODAYS_MATCHES):
        with st.container(border=True):
            col_away, col_vs, col_home = st.columns([5, 2, 5])

            state_key = f"match_select_{i}"
            if state_key not in st.session_state:
                st.session_state[state_key] = "미선택"

            # 투표율 기반 실시간 배당률 계산
            away_odds = calculate_odds(match['away_pct'])
            home_odds = calculate_odds(match['home_pct'])

            # 배당률에 비례한 최종 획득 가능 포인트 계산
            away_reward = int(base_reward_point * away_odds)
            home_reward = int(base_reward_point * home_odds)

            # 1. 원정 팀 섹션
            with col_away:
                c_a1, c_a2, c_a3 = st.columns([1, 1, 10])
                # 왼쪽 : 체크박스
                with c_a1:
                    st.checkbox("", key=f"chk_away_{i}", label_visibility="collapsed", on_change=toggle_vote, args=(i, "away"))
                # 중앙 : 팀 로고
                with c_a2:
                    st.image(match["away_logo"], width=35)
                # 오른쪽 : 정보 표시
                with c_a3:
                    away_w = match["away_recent"].count("승")
                    away_l = match["away_recent"].count("패")

                    st.markdown(
                        f"<div style='text-align: left; line-height: 1.3; Triton'>"
                        f"<span style='font-size:11px; color:#718096; background-color:#EDF2F7; padding:1px 4px; border-radius:3px; margin-right:4px; vertical-align:middle;'>{match['away_rank']}</span>"
                        f"<b style='font-size:16px; vertical-align:middle;'>{match['away']} </b>"
                        f"<span style='background-color:#E2E8F0; font-size:11px; padding:2px 4px; border-radius:3px; color:#4A5568; vertical-align:middle;'> 원정</span><br>"
                        f"<span style='font-size:12px; color:#4A5568;'>{match['away_pitcher']}</span><br>"
                        f"<span style='font-size:11px; color:#718096; background-color:#F7FAFC; padding:2px 6px; border-radius:4px; border:1px solid #E2E8F0; white-space:nowrap;'>"
                        f"타율 {match['away_team_avg']} | ERA {match['away_team_era']} | 최근 5경기 : {away_w}W {away_l}L"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            # 2. 중간 VS 및 투표율 + 포인트 획득 표시 섹션
            with col_vs:
                # 상단: 투표율 % 표시
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 12px; color: #4A5568; font-weight: bold; margin-bottom: -3px Triton;'>"
                    f"<span>{match['away_pct']}%</span>"
                    f"<span>{match['home_pct']}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # 중단: 정방향 프로그레스 바
                st.progress(match['away_pct'] / 100)

                # 하단: [신규] 예측 성공 시 획득 가능 포인트 대칭 표시
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 11px; font-weight: bold; margin-top: 2px;'>"
                    f"<span style='color:#ff4b4b;'>+{away_reward:,}P</span>"
                    f"<span style='color:#ff4b4b;'>+{home_reward:,}P</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown("<p style='text-align: center; font-size: 10px; color: #A0AEC0; margin-top: -3px; margin-bottom: 0;'>예측 현황 / 리워드</p>", unsafe_allow_html=True)

            # 3. 홈 팀 섹션
            with col_home:
                c_h3, c_h2, c_h1 = st.columns([10, 1, 1])
                # 왼쪽 : 정보 표시
                with c_h3:
                    home_w = match["home_recent"].count("승")
                    home_l = match["home_recent"].count("패")

                    st.markdown(
                        f"<div style='text-align: right; line-height: 1.3;'> "
                        f"<span style='font-size:11px; color:#718096; background-color:#EDF2F7; padding:1px 4px; border-radius:3px; margin-right:4px; vertical-align:middle;'>{match['home_rank']}</span>"
                        f"<b style='font-size:16px; vertical-align:middle;'>{match['home']}</b> "
                        f"<span style='background-color:#E2E8F0; font-size:11px; padding:2px 4px; border-radius:3px; color:#4A5568; vertical-align:middle;'>홈</span><br>"
                        f"<span style='font-size:12px; color:#4A5568;'>{match['home_pitcher']}</span><br>"
                        f"<span style='font-size:11px; color:#718096; background-color:#F7FAFC; padding:2px 6px; border-radius:4px; border:1px solid #E2E8F0; white-space:nowrap;'>"
                        f"타율 {match['home_team_avg']} | ERA {match['home_team_era']} | 최근 5경기 : {home_w}W {home_l}L"
                        f"</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                # 중앙 : 팀 로고
                with c_h2:
                    st.image(match["home_logo"], width=35)
                # 왼쪽 : 체크박스
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

            st.markdown(f"### 📑 투표 접수 확인서")
            st.markdown(f"- **현재 나의 포인트:** `💰 {st.session_state['user_points']:,} P`")
            st.markdown(f"- **모든 경기 적중 시 최대 보상:** `🔥 +{total_potential_reward:,} P`")
            st.divider()

            for pred in selected_predictions:
                st.caption(pred)
