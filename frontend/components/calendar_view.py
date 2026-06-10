"""
캘린더 컴포넌트
- 경기 일정을 테이블 형태로 시각화
- plotly 활용
"""

from datetime import datetime
import os
import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from backend.data.collect import TEAMS
from backend.data.naver_game_crawler import get_all_results

# 구단별 고유 색상 (HEX 코드)
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
    "Kiwoom": "#820024"
}

# 구단별 로고 매핑
TEAM_LOGOS = {
    "KIA": "logo_kia.svg",
    "Samsung": "logo_samsung.svg",
    "LG": "logo_lg.svg",
    "Doosan": "logo_doosan.svg",
    "KT": "logo_kt.svg",
    "SSG": "logo_ssg.svg",
    "Lotte": "logo_lotte.svg",
    "Hanwha": "logo_hanwha.svg",
    "NC": "logo_nc.svg",
    "Kiwoom": "logo_kiwoom.svg"
}

# 크롤링 원본 데이터 매핑용 보완 테이블들
TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG", "두산": "Doosan", "KT": "KT",
    "SSG": "SSG", "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

TEAM_NAME_DISPLAY = {
    "KIA": "KIA", "Samsung": "삼성", "LG": "LG", "Doosan": "두산", "KT": "KT",
    "SSG": "SSG", "Lotte": "롯데", "Hanwha": "한화", "NC": "NC", "Kiwoom": "키움"
}


def get_base64_image(file_path: str) -> str:
    """로컬 이미지 파일을 읽어 HTML src에 쓸 수 있는 Base64 문자열로 변환"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        mime_type = "image/svg+xml" if file_path.endswith(".svg") else "image/png"
        return f"data:{mime_type};base64,{encoded}"
    return ""


def draw_schedule_table(schedule_df: pd.DataFrame) -> None:
    """
    네비게이션 화살표 버튼을 이용해 8개씩 날짜 탭을 넘겨볼 수 있는 컴포넌트
    (오늘 날짜 선택 시 네이버 스포츠 실시간 API 결과 연동)
    """
    if schedule_df.empty:
        st.info("경기 일정 데이터가 존재하지 않습니다.")
        return

    LOGO_DIR = "frontend/assets"
    days_of_week = ["월", "화", "수", "목", "금", "토", "일"]

    # 0. 🗓️ 해당 데이터 월의 '말일(마지막 날)' 자동 계산
    try:
        temp_date = pd.to_datetime(schedule_df['date'])
        max_day = temp_date.dt.day.max()
        data_month = temp_date.dt.month.iloc[0]
    except Exception:
        max_day = 30
        data_month = 6

    # 1. 📅 세션 상태 초기화
    now = datetime.now()
    default_day = now.day if now.month == data_month else 2

    if "selected_day" not in st.session_state or "current_month" not in st.session_state or st.session_state.current_month != data_month:
        st.session_state.selected_day = default_day
        st.session_state.current_month = data_month

    if "current_start_day" not in st.session_state:
        calculated_start = default_day - 2
        calculated_start = max(1, min(calculated_start, max_day - 7))
        st.session_state.current_start_day = calculated_start

    # 2. 🎨 정렬 및 스타일 CSS
    st.markdown(
        """
        <style>
            div[data-testid="stHorizontalBlock"]:has(button[key^="day_btn_"]),
            div[data-testid="stHorizontalBlock"]:has(button[key^="nav_"]) {
                align-items: center !important;
                gap: 6px !important;
            }
            div[data-testid="stHorizontalBlock"] button[key^="day_btn_"] p {
                font-size: 14px !important;
                font-weight: bold !important;
            }
            div[data-testid="stHorizontalBlock"]:not(:has(button[key^="day_btn_"])):not(:has(button[key^="nav_"])) {
                align-items: center !important;
            }
            [data-testid="stImage"] {
                display: flex; justify-content: center; align-items: center; margin: 0 auto;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3. ↔️ 네비게이션 바 구성
    nav_cols = st.columns([0.8] + [1] * 8 + [0.8])
    start_d = st.session_state.current_start_day
    end_d = start_d + 7

    # ◀️ 좌측 화살표
    with nav_cols[0]:
        st.markdown("<div style='font-size:11px; visibility:hidden; margin-bottom:-4px;'>&nbsp;</div>", unsafe_allow_html=True)
        if start_d > 1:
            if st.button("◀", key="nav_prev", use_container_width=True):
                st.session_state.current_start_day = max(1, start_d - 8)
                st.rerun()
        else:
            st.button("◀", key="nav_prev_disabled", disabled=True, use_container_width=True)

    # 🔘 중앙 8개 버튼
    col_idx = 1
    for d in range(start_d, end_d + 1):
        weekday_str = days_of_week[datetime(now.year, data_month, d).weekday()]
        if d == default_day and now.month == data_month:
            weekday_str = "오늘"

        with nav_cols[col_idx]:
            is_selected = (d == st.session_state.selected_day)

            if is_selected:
                st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:bold; color:#007BFF; margin-bottom:-4px;'>{weekday_str}</div>", unsafe_allow_html=True)
                btn_label = f"{d}"
                btn_type = "primary"
            else:
                st.markdown(f"<div style='text-align:center; font-size:12px; color:#6B7280; margin-bottom:-4px;'>{weekday_str}</div>", unsafe_allow_html=True)
                btn_label = f"{d}"
                btn_type = "secondary"

            if st.button(btn_label, key=f"day_btn_{d}", type=btn_type, use_container_width=True):
                st.session_state.selected_day = d
                st.rerun()
        col_idx += 1

    # ▶️ 우측 화살표
    with nav_cols[9]:
        st.markdown("<div style='font-size:11px; visibility:hidden; margin-bottom:-4px;'>&nbsp;</div>", unsafe_allow_html=True)
        if end_d < max_day:
            if st.button("▶", key="nav_next", use_container_width=True):
                st.session_state.current_start_day = min(max_day - 7, start_d + 8)
                st.rerun()
        else:
            st.button("▶", key="nav_next_disabled", disabled=True, use_container_width=True)

    # 4. 🔍 데이터 필터링 및 크롤러 데이터 연동
    is_today_selected = (st.session_state.selected_day == default_day and now.month == data_month)

    # 💡 [핵심 연동] 선택된 날짜가 오늘이면 실시간 크롤러 데이터를 가져옵니다.
    selected_date_str = f"{now.year}-{data_month:02d}-{st.session_state.selected_day:02d}"
    today_live_results = [r for r in get_all_results() if r.get("date") == selected_date_str]

    try:
        schedule_df['parsed_date'] = pd.to_datetime(schedule_df['date'])
        filtered_df = schedule_df[schedule_df['parsed_date'].dt.day == st.session_state.selected_day]
    except Exception:
        search_str = f"{data_month:02d}/{st.session_state.selected_day:02d}"
        filtered_df = schedule_df[schedule_df['date'].astype(str).str.contains(search_str)]

    # 5. 🏟️ 경기 일정 및 결과 테이블 출력
    left_space, center_content, right_space = st.columns([0.5, 9.0, 0.5])
    with center_content:
        if filtered_df.empty and not today_live_results:
            st.markdown(f'<div style="text-align:center;padding:40px;color:#6B7280;font-size:15px;background-color:#F9FAFB;border-radius:12px;border:1px dashed #E5E7EB;">오늘은 경기가 없습니다.</div>', unsafe_allow_html=True)
            return

        html_rows = ""

        # 오늘 날짜이고 크롤링된 데이터가 존재할 때 렌더링 스위칭
        if today_live_results:
            num_rows = len(today_live_results)
            for idx_count, game in enumerate(today_live_results):
                away_key = game['away']
                home_key = game['home']

                away_name = TEAM_NAME_DISPLAY.get(away_key, away_key)
                home_name = TEAM_NAME_DISPLAY.get(home_key, home_key)

                away_hex = TEAM_COLORS.get(away_key, "#FFFFFF")
                home_hex = TEAM_COLORS.get(home_key, "#FFFFFF")

                away_logo_url = get_base64_image(os.path.join(LOGO_DIR, TEAM_LOGOS.get(away_key, "")))
                home_logo_url = get_base64_image(os.path.join(LOGO_DIR, TEAM_LOGOS.get(home_key, "")))

                # 수정
                date_str = f"{data_month:02d}/{st.session_state.selected_day:02d} ({'오늘' if is_today_selected else days_of_week[datetime(now.year, data_month, st.session_state.selected_day).weekday() % 7]})"

                # 💡 게임 상태 배지 생성
                status = game['status']
                cancel = game.get('cancel', False)
                suspended = game.get('suspended', False)

                if status == "RESULT":
                    vs_bg = "#E5E7EB"
                    vs_text = "종료"
                elif status == "LIVE" or status == "STARTED":
                    vs_bg = "#FEE2E2"
                    vs_text = "LIVE"
                elif cancel:
                    vs_bg = "#FEF9C3"
                    vs_text = "취소"
                elif suspended:
                    vs_bg = "#FEF9C3"
                    vs_text = "우천취소"
                else:
                    vs_bg = "#FFFFFF"
                    vs_text = "예정"

                # 💡 이긴 팀의 점수를 빨간색(#EF4444)으로 강조하는 로직
                away_score_color = "#EF4444" if game['winner'] == "away" else "#111111"
                home_score_color = "#EF4444" if game['winner'] == "home" else "#111111"

                # 진행 중(LIVE)일 때는 실시간으로 점수가 높은 팀을 빨간색으로
                if status == "LIVE":
                    away_score_color = "#EF4444" if game['away_score'] > game['home_score'] else "#4B5563"
                    home_score_color = "#EF4444" if game['home_score'] > game['away_score'] else "#4B5563"

                # 스코어 HTML 구조 분리 (f-string 충돌 우려 요소 제거)
                if status in ["RESULT", "LIVE"]:
                    score_html = f'<span style="font-size: 20px; font-weight: 800; color: {away_score_color};">{game["away_score"]}</span><span style="font-size: 14px; font-weight: bold; color: #9CA3AF; margin: 0 8px;">:</span><span style="font-size: 20px; font-weight: 800; color: {home_score_color};">{game["home_score"]}</span>'
                else:
                    score_html = '<span style="font-size: 13px; font-weight: bold; color: #6B7280;">VS</span>'

                row_border = "border-bottom: 1px solid #EAEAEA;" if idx_count < num_rows - 1 else ""

                # 승리팀 텍스트 굵게 강조
                away_font_weight = "800" if game['winner'] == "away" else "bold"
                home_font_weight = "800" if game['winner'] == "home" else "bold"

                # 배지 텍스트 컬러 변수화 (따옴표 충돌 방지)
                badge_color = "#EF4444" if status == "LIVE" else "#4B5563"

                row_html = (
                    f'<div style="display: flex; align-items: center; width: 100%; padding: 0px; {row_border} min-height: 65px; box-sizing: border-box;">'
                    f'  <div style="flex: 1.2; text-align: left; color: #666666; font-size: 14px; padding-left: 15px;">{date_str}</div>'
                    f'  <div style="flex: 0.8; text-align: center; font-size: 12px; font-weight: bold;">'
                    f'      <span style="background: {vs_bg}; color: {badge_color}; padding: 2px 6px; border-radius: 4px;">{vs_text}</span>'
                    f'  </div>'
                    f'  <div style="flex: 1.0; text-align: center; color: #666666; font-size: 14px;">{game["stadium"]}</div>'
                    f'  '
                    f'  <div style="flex: 3.0; display: flex; align-items: center; justify-content: flex-start; padding: 18px 0px 18px 20px; min-height: 65px; background: linear-gradient(to right, {away_hex}33 0%, {away_hex}1A 40%, rgba(255,255,255,0) 100%);">'
                    f'      <div style="width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; margin-right: 12px;"><img src="{away_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                    f'      <span style="color: #111111; font-size: 15px; font-weight: {away_font_weight};">{away_name}</span>'
                    f'  </div>'
                    f'  '
                    f'  <div style="flex: 1.4; display: flex; justify-content: center; align-items: center; min-height: 65px; background: #FFFFFF; border-left: 1px dashed #F3F4F6; border-right: 1px dashed #F3F4F6;">'
                    f'      {score_html}'
                    f'  </div>'
                    f'  '
                    f'  <div style="flex: 3.0; display: flex; align-items: center; justify-content: flex-end; padding: 18px 20px 18px 0px; min-height: 65px; background: linear-gradient(to left, {home_hex}33 0%, {home_hex}1A 40%, rgba(255,255,255,0) 100%);">'
                    f'      <div style="color: #111111; font-size: 15px; font-weight: {home_font_weight}; padding-right: 12px; display: flex; align-items: center; gap: 6px;">'
                    f'          <span style="font-size: 10px; color: {home_hex}; border: 1px solid {home_hex}60; border-radius: 3px; padding: 1px 5px; background-color: #FFFFFF; font-weight: bold; line-height: 1.1;">홈</span>'
                    f'          <span>{home_name}</span>'
                    f'      </div>'
                    f'      <div style="width: 24px; height: 24px; display: flex; justify-content: center; align-items: center;"><img src="{home_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                    f'  </div>'
                    f'</div>'
                )
                html_rows += row_html

        # 오늘이 아니거나 크롤링 데이터가 없는 과거/미래 날짜는 기존 DB 일정 표출
        else:
            num_rows = len(filtered_df)
            for idx_count, (idx, row) in enumerate(filtered_df.iterrows()):
                raw_home = str(row['home_team']).split()[0]
                raw_away = str(row['away_team']).split()[0]

                home_key = TEAM_NAME_KR.get(raw_home, raw_home)
                away_key = TEAM_NAME_KR.get(raw_away, raw_away)

                home_name = TEAM_NAME_DISPLAY.get(home_key, raw_home)
                away_name = TEAM_NAME_DISPLAY.get(away_key, raw_away)

                away_hex = TEAM_COLORS.get(away_key, "#FFFFFF")
                home_hex = TEAM_COLORS.get(home_key, "#FFFFFF")

                away_logo_url = get_base64_image(os.path.join(LOGO_DIR, TEAM_LOGOS.get(away_key, "")))
                home_logo_url = get_base64_image(os.path.join(LOGO_DIR, TEAM_LOGOS.get(home_key, "")))

                try:
                    date_val = pd.to_datetime(row['date'])
                    date_str = f"{date_val.strftime('%m/%d')} ({days_of_week[(date_val.weekday()) % 7]})"
                except:
                    date_str = f"{row['date']}"

                row_border = "border-bottom: 1px solid #EAEAEA;" if idx_count < num_rows - 1 else ""

                row_html = (
                    f'<div style="display: flex; align-items: center; width: 100%; padding: 0px; {row_border} min-height: 65px; box-sizing: border-box;">'
                    f'  <div style="flex: 1.2; text-align: left; color: #666666; font-size: 14px; padding-left: 15px;">{date_str}</div>'
                    f'  <div style="flex: 0.8; text-align: center; color: #111111; font-size: 14px; font-weight: bold;">{row["time"]}</div>'
                    f'  <div style="flex: 1.0; text-align: center; color: #666666; font-size: 14px;">{row["stadium"]}</div>'
                    f'  <div style="flex: 3.0; display: flex; align-items: center; justify-content: flex-start; padding: 18px 0px 18px 20px; min-height: 65px; background: linear-gradient(to right, {away_hex}33 0%, {away_hex}1A 40%, rgba(255,255,255,0) 100%);">'
                    f'      <div style="width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; margin-right: 12px;"><img src="{away_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                    f'      <span style="color: #111111; font-size: 15px; font-weight: bold;">{away_name}</span>'
                    f'  </div>'
                    f'  <div style="flex: 1.2; display: flex; justify-content: center; align-items: center; min-height: 65px; background: #FFFFFF;">'
                    f'      <span style="color: #4B5563; font-size: 12px; font-weight: bold; background: #FFFFFF; border: 1px solid #D1D5DB; padding: 3px 12px; border-radius: 4px; display: inline-block; min-width: 45px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); z-index: 2;">VS</span>'
                    f'  </div>'
                    f'  <div style="flex: 3.0; display: flex; align-items: center; justify-content: flex-end; padding: 18px 20px 18px 0px; min-height: 65px; background: linear-gradient(to left, {home_hex}33 0%, {home_hex}1A 40%, rgba(255,255,255,0) 100%);">'
                    f'      <div style="color: #111111; font-size: 15px; font-weight: bold; padding-right: 12px; display: flex; align-items: center; gap: 6px;">'
                    f'          <span style="font-size: 10px; color: {home_hex}; border: 1px solid {home_hex}60; border-radius: 3px; padding: 1px 5px; background-color: #FFFFFF; font-weight: bold; line-height: 1.1;">홈</span>'
                    f'          <span>{home_name}</span>'
                    f'      </div>'
                    f'      <div style="width: 24px; height: 24px; display: flex; justify-content: center; align-items: center;"><img src="{home_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                    f'  </div>'
                    f'</div>'
                )
                html_rows += row_html

        full_table_html = (
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 8px; '
            f'box-shadow: 0 1px 4px rgba(0,0,0,0.02); padding: 0px; width: 100%; box-sizing: border-box; '
            f'overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, \'Malgun Gothic\', sans-serif;">'
            f'{html_rows}'
            f'</div>'
        )
        st.markdown(full_table_html, unsafe_allow_html=True)


def draw_monthly_chart(schedule_df: pd.DataFrame) -> go.Figure:
    """
    월별 경기 수 바 차트
    """
    if schedule_df.empty:
        return go.Figure()

    df = schedule_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    daily_counts = df.groupby(df['date'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']

    fig = go.Figure(go.Bar(
        x=daily_counts['date'].astype(str),
        y=daily_counts['count'],
        marker_color='#1f77b4',
        text=daily_counts['count'],
        textposition='auto'
    ))

    fig.update_layout(
        title="일별 경기 수",
        xaxis_title="날짜",
        yaxis_title="경기 수",
        height=300
    )

    return fig
