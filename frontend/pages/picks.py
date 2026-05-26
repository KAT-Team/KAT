"""
승부예측 페이지
- 선발 투수 성적
- 팀 성적 (타율, ERA 등)
- 팀 최근 경기 전적
- 배당률 정보
- 포인트 랭킹
"""

import streamlit as st

TODAYS_MATCHES = [
    {"away": "NC", "away_logo": "frontend/assets/logo_nc.svg", "away_pitcher": "구창모", "away_pct": 36, "home": "KT", "home_logo": "frontend/assets/logo_kt.svg", "home_pitcher": "사우어", "home_pct": 64},
    {"away": "두산", "away_logo": "frontend/assets/logo_doosan.svg", "away_pitcher": "잭로그", "away_pct": 64, "home": "한화", "home_logo": "frontend/assets/logo_hanwha.svg", "home_pitcher": "화이트", "home_pct": 36},
    {"away": "SSG", "away_logo": "frontend/assets/logo_ssg.svg", "away_pitcher": "김건우", "away_pct": 62, "home": "KIA", "home_logo": "frontend/assets/logo_kia.svg", "home_pitcher": "양현종", "home_pct": 38},
    {"away": "삼성", "away_logo": "frontend/assets/logo_samsung.svg", "away_pitcher": "장찬희", "away_pct": 68, "home": "롯데", "home_logo": "frontend/assets/logo_lotte.svg", "home_pitcher": "박세웅", "home_pct": 32},
    {"away": "키움", "away_logo": "frontend/assets/logo_kiwoom.svg", "away_pitcher": "배동현", "away_pct": 38, "home": "LG", "home_logo": "frontend/assets/logo_lg.svg", "home_pitcher": "임찬규", "home_pct": 62},
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

    st.markdown("#### 📅 [5/19] 오늘의 경기 라인업")

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

            # [추가] 배당률에 비례한 최종 획득 가능 포인트 계산
            away_reward = int(base_reward_point * away_odds)
            home_reward = int(base_reward_point * home_odds)

            # 1. 원정 팀 섹션 (배당률 대신 획득 포인트 표기)

            with col_away:
                # [체크박스 | 로고 | 팀정보/배당률] 구성을 위해 3단 분할
                c_a1, c_a2, c_a3 = st.columns([1, 1, 8])
                with c_a1:
                    # [수정] on_change와 args를 추가하여 토글 기능을 연결합니다.
                    st.checkbox(
                        "",
                        key=f"chk_away_{i}",
                        label_visibility="collapsed",
                        on_change=toggle_vote,
                        args=(i, "away")
                    )
                with c_a2:
                    st.image(match["away_logo"], width=35)
                with c_a3:
                    st.markdown(
                        f"<div style='text-align: left; line-height: 1.2;'>"
                        f"<b style='font-size:16px;'>{match['away']}</b> "
                        f"<span style='color:#ff4b4b; font-size:13px; font-weight:bold; margin-left:5px;'>+{away_reward:,} P</span><br>"
                        f"<span style='font-size:12px; color:gray;'>{match['away_pitcher']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            # 2. 중간 VS 섹션
            with col_vs:
                # 양 옆에 투표율 숫자를 적어주고 가운데에 게이지 바를 배치
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 12px; color: #4A5568; font-weight: bold; margin-bottom: -5px;'>"
                    f"<span>{match['away_pct']}%</span>"
                    f"<span>{match['home_pct']}%</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                # 원정팀 투표율이 높을수록 게이지가 덜 차고, 홈팀 투표율이 높을수록 게이지가 꽉 차도록 세팅 (홈팀 비율 기준)
                st.progress(match['away_pct'] / 100)
                st.markdown("<p style='text-align: center; font-size: 11px; color: #A0AEC0; margin-top: -5px;'>예측 현황</p>", unsafe_allow_html=True)

            # 3. 홈 팀 섹션 (왼쪽: 팀명/투수, 오른쪽: 로고)
            with col_home:
                # [팀정보/배당률 | 로고 | 체크박스] 순서로 대칭 배치
                c_h3, c_h2, c_h1 = st.columns([8, 1, 1])
                with c_h3:
                    st.markdown(
                        f"<div style='text-align: right; line-height: 1.2;'> "
                        f"<span style='color:#ff4b4b; font-size:13px; font-weight:bold; margin-right:5px;'>+{home_reward:,} P</span>"
                        f"<b style='font-size:16px;'>{match['home']}</b> <span style='background-color:#EDF2F7; font-size:11px; padding:2px 4px; border-radius:3px; color:#718096; vertical-align:middle;'>홈</span><br>"
                        f"<span style='font-size:12px; color:gray;'>{match['home_pitcher']}</span>"
                        f"</div>",
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
            # 포인트 차감 없이 정상 투표 성공 메시지만 출력
            st.success("🎉 오늘의 승부예측 투표가 모두 접수되었습니다! 경기 종료 후 포인트를 확인하세요.")
            st.balloons()

            st.markdown(f"### 📑 투표 접수 확인서")
            st.markdown(f"- **현재 나의 포인트:** `💰 {st.session_state['user_points']:,} P` (차감 없음)")
            st.markdown(f"- **모든 경기 적중 시 최대 보상:** `🔥 +{total_potential_reward:,} P`")
            st.divider()

            for pred in selected_predictions:
                st.caption(pred)
