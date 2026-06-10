import os
import json
import base64
from datetime import datetime, timedelta
import streamlit as st
from backend.data.team_crawler import crawl_all_team_stats
from backend.simulation.predict import calc_win_probability
# 💡 네이버 스포츠 결과 API 함수 가져오기
from backend.data.naver_game_crawler import get_today_results

TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG",
    "두산": "Doosan", "KT": "KT", "SSG": "SSG",
    "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

@st.cache_data(ttl=3600)
def load_team_stats():
    stats = crawl_all_team_stats()
    result = {}
    for team_eng, data in stats.items():
        team_kr = data.get("team_kr", team_eng)
        result[team_kr] = {
            "avg": data.get("avg_display", ".000"),
            "era": data.get("era_display", "0.00")
        }
    return result

TEAM_STATS = load_team_stats()

TEAM_COLORS = {
    "KIA": "#EA0029",
    "Samsung": "#074CA1",
    "LG": "#C30452",
    "Doosan": "#131230",
    "KT": "#000000",
    "SSG": "#CE0E2D",
    "Lotte": "#002058",
    "Hanwha": "#FF6600",
    "NC": "#071D49",
    "Kiwoom": "#820024",
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

TODAYS_MATCHES, MATCH_DATE, DATE_CAPTION = load_todays_matches_from_json()


def get_history_file_path(date_obj) -> str:
    dir_path = os.path.join("backend", "data", "vote_history")
    os.makedirs(dir_path, exist_ok=True)
    filename = f"vote_history_{date_obj.strftime('%Y%m%d')}.json"
    return os.path.join(dir_path, filename)

def load_vote_history_from_file(date_obj) -> list:
    file_path = get_history_file_path(date_obj)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"⚠️ 기록 파일 읽기 실패: {e}")
    return []

def save_vote_history_to_file(date_obj, history_list):
    file_path = get_history_file_path(date_obj)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"⚠️ 기록 파일 저장 실패: {e}")


def show():
    cached_stats = crawl_all_team_stats()

    # 💡 실시간 네이버 경기 정보 검색 가져오기
    live_results = get_today_results()

    st.markdown("""
    <style>
        div[data-testid="stVerticalBlockBorderWithStyling"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        .feed-container {
            overflow: hidden !important;
            background-color: transparent !important;
            margin-top: 30px;
            font-family: sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

    left_space, center_content, right_content, right_space = st.columns([1.5, 6, 2, 1.5])

    if "total_match_votes" not in st.session_state:
        st.session_state.total_match_votes = {
            i: {"away": 10, "home": 10} for i in range(len(TODAYS_MATCHES))
        }

    if "user_current_picks" not in st.session_state:
        st.session_state.user_current_picks = {i: "none" for i in range(len(TODAYS_MATCHES))}

    if "vote_history" not in st.session_state:
        st.session_state.vote_history = load_vote_history_from_file(MATCH_DATE)

    def on_away_change(index):
        key = f"chk_away_raw_{index}"
        if st.session_state[key]:
            st.session_state.user_current_picks[index] = "away"
            st.session_state[f"chk_home_raw_{index}"] = False
        else:
            if st.session_state.user_current_picks[index] == "away":
                st.session_state.user_current_picks[index] = "none"

    def on_home_change(index):
        key = f"chk_home_raw_{index}"
        if st.session_state[key]:
            st.session_state.user_current_picks[index] = "home"
            st.session_state[f"chk_away_raw_{index}"] = False
        else:
            if st.session_state.user_current_picks[index] == "home":
                st.session_state.user_current_picks[index] = "none"

    @st.dialog("👤 참여자 닉네임 등록")
    def open_nickname_dialog():
        st.write("예측 피드에 기록될 닉네임을 입력하세요. (중복 닉네임은 불가능합니다.)")
        input_nickname = st.text_input("닉네임 입력 (최대 10자)", max_chars=10, placeholder="").strip()

        file_history = load_vote_history_from_file(MATCH_DATE)
        existing_nicknames = [record["nickname"] for record in file_history]

        if st.button("예측 제출 및 등록하기", type="primary", use_container_width=True):
            if not input_nickname:
                st.error("⚠️ 닉네임을 입력하지 않았습니다.")
                return

            if input_nickname in existing_nicknames:
                st.error(f"❌ '{input_nickname}'은(는) 이미 등록된 닉네임입니다. 다른 닉네임을 사용해주세요.")
                return

            current_submission_picks = []
            submission_total_points = 0

            for idx in range(len(TODAYS_MATCHES)):
                match = TODAYS_MATCHES[idx]
                user_pick = st.session_state.user_current_picks[idx]
                votes_data = st.session_state.total_match_votes[idx]

                try:
                    # 🛠️ [수정 완료] 아규먼트 배치 순서 교정: (home, away)
                    prob_result = calc_win_probability(
                        match["home_eng"], match["away_eng"], "", "", 50, 50
                    )
                    away_ratio_num = max(1, prob_result["away_prob"])
                    home_ratio_num = max(1, prob_result["home_prob"])
                except Exception:
                    away_votes = votes_data["away"]
                    home_votes = votes_data["home"]
                    away_ratio_num = max(1, int(round((away_votes / (away_votes + home_votes)) * 100)))
                    home_ratio_num = max(1, 100 - away_ratio_num)

                calc_away_p = int(100 + (home_ratio_num / away_ratio_num) * 100)
                calc_home_p = int(100 + (away_ratio_num / home_ratio_num) * 100)

                if user_pick == "away":
                    chosen_team = match["away"]
                    chosen_p = calc_away_p
                    st.session_state.total_match_votes[idx]["away"] += 1
                else:
                    chosen_team = match["home"]
                    chosen_p = calc_home_p
                    st.session_state.total_match_votes[idx]["home"] += 1

                current_submission_picks.append(f"<b>{chosen_team}</b>({chosen_p}P)")
                submission_total_points += chosen_p

            new_record = {
                "no": len(file_history) + 1,
                "nickname": input_nickname,
                "picks": " , ".join(current_submission_picks),
                "total_points": submission_total_points
            }

            file_history.append(new_record)
            save_vote_history_to_file(MATCH_DATE, file_history)
            st.session_state.vote_history = file_history

            for idx in range(len(TODAYS_MATCHES)):
                st.session_state.user_current_picks[idx] = "none"
                if f"chk_away_raw_{idx}" in st.session_state:
                    st.session_state[f"chk_away_raw_{idx}"] = False
                if f"chk_home_raw_{idx}" in st.session_state:
                    st.session_state[f"chk_home_raw_{idx}"] = False

            st.success(f"🎉 {input_nickname}님의 소중한 예측이 등록되었습니다!")
            st.rerun()

    # 2️⃣ 중앙 콘텐츠 영역
    with center_content:
        st.markdown("### 🔮 승부 예측")
        st.markdown(f"<p style='font-size: 14px; color: gray;'>{DATE_CAPTION}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 📅 [{MATCH_DATE.month}/{MATCH_DATE.day}] 예정된 경기 라인업")

        if not TODAYS_MATCHES:
            st.info("당분간 예정된 KBO 경기 일정이 없습니다.")
            return

        for i, match in enumerate(TODAYS_MATCHES):
            votes_data = st.session_state.total_match_votes[i]
            away_votes = votes_data["away"]
            home_votes = votes_data["home"]
            total_votes = away_votes + home_votes

            try:
                # 🛠️ [수정 완료] 아규먼트 배치 순서 교정: (home, away)
                prob_result = calc_win_probability(
                    match["home_eng"], match["away_eng"], "", "", 50, 50
                )
                away_ratio_num = max(1, prob_result["away_prob"])
                home_ratio_num = max(1, prob_result["home_prob"])
            except Exception:
                away_ratio_num = max(1, int(round((away_votes / total_votes) * 100)))
                home_ratio_num = max(1, 100 - away_ratio_num)

            away_point_str = f"+{int(100 + (home_ratio_num / away_ratio_num) * 100)}P"
            home_point_str = f"+{int(100 + (away_ratio_num / home_ratio_num) * 100)}P"

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

            # 💡 [추가] 실시간 매칭 상태 추출 파트
            game_status_text = f"{match['time']} | {match['stadium']}"
            target_live = next((g for g in live_results if g["home"] == match["home_eng"] and g["away"] == match["away_eng"]), None)

            if target_live:
                if target_live["status"] == "RESULT":
                    game_status_text = f"경기종료 | {target_live['away_score']} : {target_live['home_score']}"
                elif target_live["status"] == "LIVE":
                    game_status_text = f"진행중 ({target_live['away_score']}:{target_live['home_score']}) | {match['stadium']}"

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
                    st.checkbox("", key=f"chk_away_raw_{i}", label_visibility="collapsed", on_change=on_away_change, args=(i,))

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
                            <span style="font-size: 12px; font-weight: bold; color: #4A5568;">{game_status_text}</span>
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
                    st.checkbox("", key=f"chk_home_raw_{i}", label_visibility="collapsed", on_change=on_home_change, args=(i,))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("승부예측 제출하기", type="primary", use_container_width=True):
            submit_count = sum(1 for idx in range(len(TODAYS_MATCHES)) if st.session_state.user_current_picks[idx] in ["away", "home"])
            if submit_count == len(TODAYS_MATCHES):
                open_nickname_dialog()
            else:
                st.warning("⚠️ 모든 경기의 승부를 마킹한 후 제출해 주세요.")

    # 3️⃣ 우측 대시보드 영역 (나의 예측 현황)
    with right_content:
        st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 나의 예측 현황")

        submit_count = sum(1 for idx in range(len(TODAYS_MATCHES)) if st.session_state.user_current_picks[idx] in ["away", "home"])

        if submit_count == 0:
            st.markdown('<div style="border: 2px dashed #E2E8F0; border-radius: 12px; padding: 40px 16px; text-align: center; color: #A0AEC0; font-size: 14px; margin-top: 26px;">예측 마킹 대기 중 🕒</div>', unsafe_allow_html=True)
        else:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

            summary_inner_html = ""
            total_potential_points = 0

            for i, match in enumerate(TODAYS_MATCHES):
                user_pick = st.session_state.user_current_picks[i]
                if user_pick == "none":
                    continue

                try:
                    prob_result = calc_win_probability(
                        match["home_eng"], match["away_eng"], "", "", 50, 50
                    )
                    away_ratio_num = max(1, prob_result["away_prob"])
                    home_ratio_num = max(1, prob_result["home_prob"])
                except Exception:
                    votes_data = st.session_state.total_match_votes[i]
                    away_ratio_num = max(1, int(round((votes_data["away"] / (votes_data["away"] + votes_data["home"])) * 100)))
                    home_ratio_num = max(1, 100 - away_ratio_num)

                calc_away_p = int(100 + (home_ratio_num / away_ratio_num) * 100)
                calc_home_p = int(100 + (away_ratio_num / home_ratio_num) * 100)

                if user_pick == "away":
                    team_name, team_color, current_p = match["away"], TEAM_COLORS.get(match["away_eng"], "#1A202C"), calc_away_p
                else:
                    team_name, team_color, current_p = match["home"], TEAM_COLORS.get(match["home_eng"], "#1A202C"), calc_home_p

                total_potential_points += current_p

                summary_inner_html += f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #E2E8F0; background: transparent;"><div style="display: flex; flex-direction: column;"><span style="font-size: 11px; color: #718096;">{match["time"]} [{match["stadium"]}]</span><span style="font-size: 13px; color: #4A5568; font-weight: 500;">{match["away"]} vs {match["home"]}</span></div><div style="text-align: right; line-height: 1.3;"><span style="font-size: 14px; color: {team_color}; font-weight: bold;">{team_name}</span><br><span style="font-size: 11px; color: #3182CE; font-weight: bold;">+{current_p}P</span></div></div>'

            summary_final_html = f'<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; font-family: sans-serif;">{summary_inner_html}<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 4px;"><span style="font-size: 14px; font-weight: bold; color: #2D3748;">선택 완료 경기</span><span style="font-size: 15px; font-weight: bold; color: #2D3748;">{submit_count} / {len(TODAYS_MATCHES)}</span></div><div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;"><span style="font-size: 14px; font-weight: bold; color: #2D3748;">최대 획득 포인트</span><span style="font-size: 18px; font-weight: 800; color: #3182CE;">{total_potential_points:,} P</span></div></div>'
            st.markdown(summary_final_html, unsafe_allow_html=True)

    # 4️⃣ 📜 실시간 참여 유저 예측 현황 피드 (순수 스트림릿 데이터프레임 기반 정산)
    st.markdown("---")

    left_space, center_content, right_space = st.columns([1.5, 8, 1.5])
    with center_content:
        st.markdown("### 📜 승부예측 유저 참여 현황")
        st.markdown("<p style='font-size: 14px; color: gray;'>유저들이 등록한 승부예측 기록과 실시간 정산 결과입니다. (최근 제출 순서 상단 정렬)</p>", unsafe_allow_html=True)

        if not st.session_state.vote_history:
            st.info("아직 제출된 승부예측 히스토리가 존재하지 않습니다. 첫 번째 예측 기록의 주인공이 되어보세요!")
        else:
            table_data = []

            for record in st.session_state.vote_history[::-1]:
                pts = record.get("total_points", 0)
                formatted_pts = f"{pts:,} P" if pts > 0 else "-"

                user_earned_points = 0
                raw_picks = record.get("picks", "")

                clean_picks_text = raw_picks.replace("<b>", "").replace("</b>", "")
                pick_items = [p.strip() for p in clean_picks_text.split(",") if p.strip()]

                for item in pick_items:
                    if "(" in item and ")" in item:
                        try:
                            team_part = item.split("(")[0].strip()
                            point_part = item.split("(")[1].replace("P)", "").replace(",", "").strip()
                            match_point = int(point_part)
                        except (ValueError, IndexError):
                            continue

                        user_pick_eng = TEAM_NAME_KR.get(team_part, team_part)

                        target_live = next((g for g in live_results if g["status"] == "RESULT" and (g["home"] == user_pick_eng or g["away"] == user_pick_eng)), None)

                        if target_live:
                            if target_live["winner"] == "home" and target_live["home"] == user_pick_eng:
                                user_earned_points += match_point
                            elif target_live["winner"] == "away" and target_live["away"] == user_pick_eng:
                                user_earned_points += match_point

                table_data.append({
                    "순번": record["no"],
                    "참여자 닉네임": f"👤 {record['nickname']}",
                    "선택 구단 및 참여 시점 배당 정보": clean_picks_text,
                    "최대 예상 리워드": formatted_pts,
                    "획득한 리워드": f"{user_earned_points:,} P" if user_earned_points > 0 else "0 P"
                })

            st.dataframe(
                data=table_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "순번": st.column_config.NumberColumn(alignment="center"),
                    "최대 예상 리워드": st.column_config.TextColumn(alignment="center"),
                    "획득한 리워드": st.column_config.TextColumn(alignment="center"),
                }
            )
