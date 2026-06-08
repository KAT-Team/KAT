"""
승부예측 페이지
- kbo_schedule.json 기반 미래 날짜 자동 탐색 기능 유지
- calendar_view.py의 검증된 base64 로고 인코딩 기술을 도입하여 로고 깨짐 전면 해결
- HTML 통합형 그라데이션 박스로 테두리 찢어짐 버그 원천 차단
- 우측 실시간 픽 현황 및 리워드 대시보드 추가
"""

import os
import json
import base64
from datetime import datetime, timedelta
import streamlit as st

TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG",
    "두산": "Doosan", "KT": "KT", "SSG": "SSG",
    "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

#  팀별 성적 데이터베이스 -> crawler.py에서 팀 기록 받아와야함
TEAM_STATS = {
    "KIA": {"avg": ".291", "era": "3.95"},
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
TEAM_COLORS = {
    "KIA": "#EA0029",     # 기아 빨강
    "Samsung": "#074CA1", # 삼성 파랑
    "LG": "#C30452",      # LG 빨강
    "Doosan": "#131230",  # 두산 네이비
    "KT": "#000000",      # KT 검정
    "SSG": "#CE0E2D",     # SSG 빨강
    "Lotte": "#002058",   # 롯데 네이비
    "Hanwha": "#FF6600",  # 한화 주황
    "NC": "#071D49",      # NC 네이비
    "Kiwoom": "#820024",  # 키움 와인
}


def get_base64_image(file_path: str) -> str:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        mime_type = "image/svg+xml" if file_path.endswith(".svg") else "image/png"
        return f"data:{mime_type};base64,{encoded}"
    return ""


def load_todays_matches_from_json():
    json_path = os.path.join("backend", "data", "kbo_schedule.json")
    if not os.path.exists(json_path) and os.path.exists("kbo_schedule.json"):
        json_path = "kbo_schedule.json"

    if not os.path.exists(json_path):
        st.error(f"🚨 스케줄 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_path}")
        return [], datetime.now(), ""

    with open(json_path, "r", encoding="utf-8") as f:
        all_schedules = json.load(f)

    base_date = datetime.now()
    weeks = ["월", "화", "수", "목", "금", "토", "일"]

    todays_raw_matches = []
    target_date = base_date

    for i in range(7):
        current_check_date = base_date + timedelta(days=i)
        week_kr = weeks[current_check_date.weekday()]
        match_date_str = f"{current_check_date.month}월 {current_check_date.month:02d}.{current_check_date.day:02d}({week_kr})"
        filtered_matches = [m for m in all_schedules if m.get("날짜") == match_date_str]

        if filtered_matches:
            todays_raw_matches = filtered_matches
            target_date = current_check_date
            break

    date_caption = "오늘의 경기 스케줄과 팀 전력 정보입니다."

    todays_matches = []
    for match in todays_raw_matches:
        teams = match["경기"].split(" vs ")
        if len(teams) != 2:
            continue

        away_team = teams[0].strip()
        home_team = teams[1].strip()

        away_eng = TEAM_NAME_KR.get(away_team, "KIA")
        home_eng = TEAM_NAME_KR.get(home_team, "Kiwoom")

        away_stat = TEAM_STATS.get(away_team, {"avg": ".000", "era": "0.00"})
        home_stat = TEAM_STATS.get(home_team, {"avg": ".000", "era": "0.00"})

        todays_matches.append({
            "away": away_team,
            "away_eng": away_eng,
            "away_logo": f"frontend/assets/logo_{away_eng.lower()}.svg",
            "away_avg": away_stat["avg"],
            "away_era": away_stat["era"],

            "home": home_team,
            "home_eng": home_eng,
            "home_logo": f"frontend/assets/logo_{home_eng.lower()}.svg",
            "home_avg": home_stat["avg"],
            "home_era": home_stat["era"],

            "time": match.get("시간", "18:30"),
            "stadium": match.get("구장", "야구장")
        })

    return todays_matches, target_date, date_caption


# 데이터 사전 로드
TODAYS_MATCHES, MATCH_DATE, DATE_CAPTION = load_todays_matches_from_json()

def show():
    left_space, center_content, right_content, right_space = st.columns([1.5, 6, 2, 1.5])

    # 1️⃣ [세션 상태 초기화] 변수들이 없으면 안전하게 생성
    if "total_match_votes" not in st.session_state:
        st.session_state.total_match_votes = {
            i: {"away": 5, "home": 5} for i in range(len(TODAYS_MATCHES))
        }

    # 유저가 화면에서 마킹하는 임시 저장소
    if "user_current_picks" not in st.session_state:
        st.session_state.user_current_picks = {i: "none" for i in range(len(TODAYS_MATCHES))}

    # 실제 '제출'이 완료되었는지 여부를 추적하는 플래그
    if "vote_submitted" not in st.session_state:
        st.session_state.vote_submitted = False

    # 🔥 [신규] 제출하는 순간의 팀과 포인트 스냅샷을 저장할 저장소
    if "submitted_picks_info" not in st.session_state:
        st.session_state.submitted_picks_info = []

    # 💡 [콜백 함수 정의] 위젯 값이 바뀔 때 락(Lock) 없이 안전하게 세션과 싱크를 맞춤
    def on_away_change(index):
        key = f"chk_away_raw_{index}"
        if st.session_state[key]: # 원정을 체크했다면
            st.session_state.user_current_picks[index] = "away"
            st.session_state[f"chk_home_raw_{index}"] = False # 홈 체크 해제
        else:
            if st.session_state.user_current_picks[index] == "away":
                st.session_state.user_current_picks[index] = "none"

    def on_home_change(index):
        key = f"chk_home_raw_{index}"
        if st.session_state[key]: # 홈을 체크했다면
            st.session_state.user_current_picks[index] = "home"
            st.session_state[f"chk_away_raw_{index}"] = False # 원정 체크 해제
        else:
            if st.session_state.user_current_picks[index] == "home":
                st.session_state.user_current_picks[index] = "none"

    # 2️⃣ 중앙 콘텐츠 영역: 경기 대진 목록 및 체크박스
    with center_content:
        st.markdown("### 🔮 승부 예측")
        st.markdown(f"<p style='font-size: 14px; color: gray;'>{DATE_CAPTION}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 📅 [6/9] 예정된 경기 라인업 헤더가 우측 '나의 예측 현황'과 정확히 같은 높이에 서게 됩니다.
        st.markdown(f"#### 📅 [{MATCH_DATE.month}/{MATCH_DATE.day}] 예정된 경기 라인업")

        if not TODAYS_MATCHES:
            st.info("당분간 예정된 KBO 경기 일정이 없습니다.")
            return

        # 💡 [요청 반영] 성공 안내 문구(st.success) 줄을 깨끗하게 삭제했습니다.

        # 경기 라인업 카드 출력
        for i, match in enumerate(TODAYS_MATCHES):
            votes_data = st.session_state.total_match_votes[i]
            away_votes = votes_data["away"]
            home_votes = votes_data["home"]
            total_votes = away_votes + home_votes

            away_ratio_num = int(round((away_votes / total_votes) * 100))
            home_ratio_num = 100 - away_ratio_num

            away_point_str = f"+{int(100 + (home_votes / away_votes) * 100)}P"
            home_point_str = f"+{int(100 + (away_votes / home_votes) * 100)}P"

            COLOR_BLUE = "#3182CE"
            COLOR_BLACK = "#1A202C"
            away_bar_color = COLOR_BLUE if away_ratio_num >= home_ratio_num else COLOR_BLACK
            home_bar_color = COLOR_BLUE if home_ratio_num > away_ratio_num else COLOR_BLACK

            away_hex = TEAM_COLORS.get(match["away_eng"], "#FFFFFF")
            home_hex = TEAM_COLORS.get(match["home_eng"], "#FFFFFF")
            away_bg_start = f"{away_hex}1A"
            home_bg_start = f"{home_hex}1A"

            away_logo_url = get_base64_image(match["away_logo"])
            home_logo_url = get_base64_image(match["home_logo"])
            away_img_html = f'<img src="{away_logo_url}" width="34" height="34" style="object-fit: contain;">' if away_logo_url else '⚾'
            home_img_html = f'<img src="{home_logo_url}" width="34" height="34" style="object-fit: contain;">' if home_logo_url else '⚾'

            st.markdown(f"""
            <style>
                div[data-testid="stVerticalBlockBorderWithStyling"]:nth-of-type({i+1}) {{
                    background: linear-gradient(90deg, {away_bg_start} 0%, rgba(255,255,255,1) 50%, {home_bg_start} 100%) !important;
                    border: 1px solid #E2E8F0 !important;
                    border-radius: 12px !important;
                    padding: 14px 18px !important;
                    margin-bottom: 16px !important;
                    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.02) !important;
                }}
            </style>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                col_chk_away, col_team_away, col_center, col_team_home, col_chk_home = st.columns([0.6, 2.6, 3.6, 2.6, 0.6])

                with col_chk_away:
                    chk_away_key = f"chk_away_raw_{i}"
                    is_disabled = st.session_state.vote_submitted

                    st.checkbox(
                        "",
                        key=chk_away_key,
                        disabled=is_disabled,
                        label_visibility="collapsed",
                        on_change=on_away_change,
                        args=(i,)
                    )

                with col_team_away:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px; font-family: sans-serif;">
                        <div style="display: flex; justify-content: center; align-items: center; width: 34px; height: 34px;">{away_img_html}</div>
                        <div style="line-height: 1.4;">
                            <span style="font-size: 15px; font-weight: bold; color: #1A202C;">{match['away']}</span>
                            <span style="color: #718096; font-size: 10px; background-color: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 3px;">원정</span><br>
                            <span style="font-size: 11px; color: #4A5568; white-space: nowrap;">타율 {match['away_avg']} | ERA {match['away_era']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_center:
                    st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; width: 100%; font-family: sans-serif;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%;">
                            <span style="font-size: 12px; font-weight: bold; color: #4A5568;">{match['time']}</span>
                            <span style="font-size: 11px; color: #718096; font-weight: 500;"> | </span>
                            <span style="font-size: 11px; color: #718096; font-weight: 500;">{match['stadium']}</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 8px;">
                            <div style="text-align: right; min-width: 40px; font-size: 12px; font-weight: bold; color: #2D3748; line-height: 1.1;">{away_ratio_num}%<br><span style="font-size: 9px; color: #3182CE; font-weight: 600;">{away_point_str}</span></div>
                            <div style="flex-grow: 1; height: 6px; background: linear-gradient(90deg, {away_bar_color} 0%, {away_bar_color} {away_ratio_num}%, {home_bar_color} {away_ratio_num}%, {home_bar_color} 100%); border-radius: 3px;"></div>
                            <div style="text-align: left; min-width: 40px; font-size: 12px; font-weight: bold; color: #2D3748; line-height: 1.1;">{home_ratio_num}%<br><span style="font-size: 9px; color: #3182CE; font-weight: 600;">{home_point_str}</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_team_home:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; text-align: right; font-family: sans-serif;">
                        <div style="line-height: 1.4;">
                            <span style="color: #718096; font-size: 10px; background-color: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 3px;">홈</span>
                            <span style="font-size: 15px; font-weight: bold; color: #1A202C;">{match['home']}</span><br>
                            <span style="font-size: 11px; color: #4A5568; white-space: nowrap;">타율 {match['home_avg']} | ERA {match['home_era']}</span>
                        </div>
                        <div style="display: flex; justify-content: center; align-items: center; width: 34px; height: 34px;">{home_img_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_chk_home:
                    chk_home_key = f"chk_home_raw_{i}"
                    st.checkbox(
                        "",
                        key=chk_home_key,
                        disabled=is_disabled,
                        label_visibility="collapsed",
                        on_change=on_home_change,
                        args=(i,)
                    )

        st.markdown("<br>", unsafe_allow_html=True)

        # 제출 버튼 제어
        button_label = "제출이 완료되었습니다" if st.session_state.vote_submitted else "승부예측 제출하기"

        if st.button(button_label, type="primary", use_container_width=True, disabled=st.session_state.vote_submitted):
            submit_count = 0
            for idx in range(len(TODAYS_MATCHES)):
                if st.session_state.user_current_picks[idx] in ["away", "home"]:
                    submit_count += 1

            if submit_count == len(TODAYS_MATCHES):
                temp_snapshot = []
                for idx in range(len(TODAYS_MATCHES)):
                    match = TODAYS_MATCHES[idx]
                    final_pick = st.session_state.user_current_picks[idx]
                    votes_data = st.session_state.total_match_votes[idx]

                    calc_away_p = int(100 + (votes_data["home"] / votes_data["away"]) * 100)
                    calc_home_p = int(100 + (votes_data["away"] / votes_data["home"]) * 100)

                    if final_pick == "away":
                        chosen_team = match["away"]
                        chosen_eng = match["away_eng"]
                        allocated_point = calc_away_p
                    else:
                        chosen_team = match["home"]
                        chosen_eng = match["home_eng"]
                        allocated_point = calc_home_p

                    temp_snapshot.append({
                        "time": match["time"],
                        "stadium": match["stadium"],
                        "title": f"{match['away']} vs {match['home']}",
                        "team": chosen_team,
                        "team_eng": chosen_eng,
                        "point": allocated_point
                    })

                for idx in range(len(TODAYS_MATCHES)):
                    final_pick = st.session_state.user_current_picks[idx]
                    if final_pick == "away":
                        st.session_state.total_match_votes[idx]["away"] += 1
                    elif final_pick == "home":
                        st.session_state.total_match_votes[idx]["home"] += 1

                st.session_state.submitted_picks_info = temp_snapshot
                st.session_state.vote_submitted = True
                st.rerun()
            else:
                st.warning("⚠️ 모든 경기의 승부를 예측해주세요.")


    # 3️⃣ 👉 [우측 사이드 대시보드 영역 (3.5)]
    with right_content:
        # 💡 왼쪽 레이아웃의 타이틀/설명글 높이만큼 공백을 주어 '나의 예측 현황'을 아래로 밀어내 눈높이를 맞춥니다.
        st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)

        st.markdown("### 📊 나의 예측 현황")

        if not st.session_state.vote_submitted:
            st.markdown("<p style='font-size: 14px; color: gray;'>경기를 선택하고 하단의 제출하기 버튼을 누르면 예측 현황 대시보드가 활성화됩니다.</p>", unsafe_allow_html=True)
            st.markdown('<div style="border: 2px dashed #E2E8F0; border-radius: 12px; padding: 40px 16px; text-align: center; color: #A0AEC0; font-size: 14px; margin-top: 26px;">예측 제출 대기 중 🕒</div>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 14px; color: gray;'>선택한 구단과 획득 가능한 리워드 정보입니다.</p>", unsafe_allow_html=True)

            # 왼쪽 라인업 카드들과의 간격을 고려해 미세 조정한 여백
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            summary_html = '<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; font-family: sans-serif;">'

            total_potential_points = 0

            # 🔥 [실시간 렌더링] total_match_votes 데이터를 실시간 조회하여 배당 포인트를 매번 재계산합니다.
            for i, match in enumerate(TODAYS_MATCHES):
                user_pick = st.session_state.user_current_picks[i]
                votes_data = st.session_state.total_match_votes[i]

                # 실시간 배당 포인트 수식 적용
                calc_away_p = int(100 + (votes_data["home"] / votes_data["away"]) * 100)
                calc_home_p = int(100 + (votes_data["away"] / votes_data["home"]) * 100)

                if user_pick == "away":
                    team_name = match["away"]
                    team_color = TEAM_COLORS.get(match["away_eng"], "#1A202C")
                    current_p = calc_away_p
                else:
                    team_name = match["home"]
                    team_color = TEAM_COLORS.get(match["home_eng"], "#1A202C")
                    current_p = calc_home_p

                total_potential_points += current_p

                team_display = f'<b style="color: {team_color};">{team_name}</b>'
                point_display = f'<span style="color: #3182CE; font-weight: bold;">+{current_p}P</span>'

                summary_html += '<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #E2E8F0;">'
                summary_html += '<div style="display: flex; flex-direction: column;">'
                summary_html += f'<span style="font-size: 11px; color: #718096;">{match["time"]} [{match["stadium"]}]</span>'
                summary_html += f'<span style="font-size: 13px; color: #4A5568; font-weight: 500;">{match["away"]} vs {match["home"]}</span>'
                summary_html += '</div>'
                summary_html += '<div style="text-align: right; line-height: 1.3;">'
                summary_html += f'<span style="font-size: 14px;">{team_display}</span><br>'
                summary_html += f'<span style="font-size: 11px;">{point_display}</span>'
                summary_html += '</div>'
                summary_html += '</div>'

            summary_html += '<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">'
            summary_html += '<span style="font-size: 14px; font-weight: bold; color: #2D3748;">최대 획득 포인트</span>'
            summary_html += f'<span style="font-size: 18px; font-weight: 800; color: #3182CE;">{total_potential_points:,} P</span>'
            summary_html += '</div>'
            summary_html += '</div>'

            st.markdown(summary_html, unsafe_allow_html=True)
