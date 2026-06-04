"""
캘린더 컴포넌트
- 경기 일정을 테이블 형태로 시각화
- plotly 활용
"""

import datetime
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from backend.data.collect import TEAMS

# 구단별 고유 색상
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


def draw_schedule_table(schedule_df: pd.DataFrame) -> None:
    """
    네이버 스포츠처럼 좌우 화살표 버튼을 이용해 12개씩 날짜 탭을 넘겨볼 수 있는 컴포넌트
    """
    if schedule_df.empty:
        st.info("경기 일정 데이터가 존재하지 않습니다.")
        return

    LOGO_DIR = "frontend/assets"
    days_of_week = ["월", "화", "수", "목", "금", "토", "일"]

    # 1. 📅 세션 상태 초기화 (기본 선택일 및 슬라이드 시작일 관리)
    now = datetime.datetime.now()
    default_day = now.day if now.month == 6 else 2

    if "selected_day" not in st.session_state:
        st.session_state.selected_day = default_day

    # 현재 화면에 보여줄 12개 버튼의 시작 날짜 (기본값: 1일)
    if "current_start_day" not in st.session_state:
        # 오늘 날짜가 속한 구간으로 시작일을 자동 세팅해 주는 센스
        if default_day <= 12:
            st.session_state.current_start_day = 1
        elif default_day <= 24:
            st.session_state.current_start_day = 13
        else:
            st.session_state.current_start_day = 25

    # 2. 🎨 정렬 및 버튼 글씨 크기 제어 CSS 수정
    st.markdown(
        """
        <style>
            /* 버튼들이 찌그러지지 않고 나란히 수평 정렬되도록 고정 */
            div[data-testid="stHorizontalBlock"]:has(button[key^="day_btn_"]),
            div[data-testid="stHorizontalBlock"]:has(button[key^="nav_"]) {
                align-items: center !important;
                gap: 4px !important;
            }
            /* 🌟 [핵심 수정] 날짜 버튼 내부의 글씨 크기와 행간을 압축하여 축소 */
            div[data-testid="stHorizontalBlock"] button[key^="day_btn_"] p {
                font-size: 11px !important;
                line-height: 1.3 !important;
                white-space: pre-line !important;
            }
            /* 경기 내용 수직 중앙 정렬 */
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

    # 3. ↔️ 네이버 스포츠 스타일 슬라이드 네비게이션 바 구성 (좌측 화살표 여백 보정형)
    # 좌측 화살표 컬럼 비율을 0.6에서 0.8로 미세하게 넓혀 좌우 시각적 대칭을 맞춥니다.
    nav_cols = st.columns([0.8] + [1] * 12 + [0.6])

    start_d = st.session_state.current_start_day
    end_d = min(start_d + 11, 30)

    # ◀️ 좌측 화살표 버튼 (더 투명하고 균형 잡힌 상단 여백)
    with nav_cols[0]:
        st.markdown("<div style='font-size:11px; visibility:hidden; margin-bottom:-4px;'>&nbsp;</div>", unsafe_allow_html=True)
        if start_d > 1:
            if st.button("◀", key="nav_prev", use_container_width=True):
                st.session_state.current_start_day = max(1, start_d - 12)
                st.rerun()
        else:
            st.button("◀", key="nav_prev_disabled", disabled=True, use_container_width=True)

    # 🔘 중앙 12개 동적 날짜 버튼 생성
    col_idx = 1
    for d in range(start_d, end_d + 1):
        weekday_str = days_of_week[(d - 1) % 7]
        if d == default_day:
            weekday_str = "오늘"

        with nav_cols[col_idx]:
            is_selected = (d == st.session_state.selected_day)

            # 요일 마크다운 출력
            if is_selected:
                st.markdown(f"<div style='text-align:center; font-size:11px; font-weight:bold; color:#007BFF; margin-bottom:-4px;'>{weekday_str}</div>", unsafe_allow_html=True)
                btn_label = f"{d}"
                btn_type = "primary"
            else:
                st.markdown(f"<div style='text-align:center; font-size:11px; color:#6B7280; margin-bottom:-4px;'>{weekday_str}</div>", unsafe_allow_html=True)
                btn_label = f"{d}"
                btn_type = "secondary"

            if st.button(btn_label, key=f"day_btn_{d}", type=btn_type, use_container_width=True):
                st.session_state.selected_day = d
                st.rerun()
        col_idx += 1

    # 빈 칸 채우기
    while col_idx <= 12:
        with nav_cols[col_idx]:
            st.write("")
        col_idx += 1

    # ▶️ 우측 화살표 버튼
    with nav_cols[13]:
        st.markdown("<div style='font-size:11px; visibility:hidden; margin-bottom:-4px;'>&nbsp;</div>", unsafe_allow_html=True)
        if end_d < 30:
            if st.button("▶", key="nav_next", use_container_width=True):
                st.session_state.current_start_day = start_d + 12
                st.rerun()
        else:
            st.button("▶", key="nav_next_disabled", disabled=True, use_container_width=True)

    # 4. 🔍 선택된 날짜에 맞는 데이터 필터링
    try:
        schedule_df['parsed_date'] = pd.to_datetime(schedule_df['date'])
        filtered_df = schedule_df[schedule_df['parsed_date'].dt.day == st.session_state.selected_day]
    except Exception:
        search_str = f"06/{st.session_state.selected_day:02d}"
        filtered_df = schedule_df[schedule_df['date'].astype(str).str.contains(search_str)]

    # 4. 🏟️ 경기 일정 카드 테이블 출력 (검은 박스 방지 완전 평탄화 버전)
    left_space, center_content, right_space = st.columns([0.5, 9.0, 0.5])

    with center_content:
        # 데이터프레임 변수명 자동 매핑
        target_df = locals().get('filtered_df', locals().get('day_df', locals().get('df', None)))

        if target_df is None or target_df.empty:
            st.markdown(f'<div style="text-align:center;padding:40px;color:#6B7280;font-size:15px;background-color:#F9FAFB;border-radius:12px;border:1px dashed #E5E7EB;">오늘은 경기가 없습니다.</div>', unsafe_allow_html=True)
            return

        html_rows = ""
        num_rows = len(target_df)
        days_of_week = ["월", "화", "수", "목", "금", "토", "일"]

        for idx_count, (idx, row) in enumerate(target_df.iterrows()):
            raw_home = str(row['home_team']).split()[0]
            raw_away = str(row['away_team']).split()[0]

            home_key = TEAM_NAME_KR.get(raw_home, raw_home)
            away_key = TEAM_NAME_KR.get(raw_away, raw_away)

            home_name = TEAM_NAME_DISPLAY.get(home_key, raw_home)
            away_name = TEAM_NAME_DISPLAY.get(away_key, raw_away)

            # 로고 이미지 경로 설정
            away_logo_file = TEAM_LOGOS.get(away_key, "")
            home_logo_file = TEAM_LOGOS.get(home_key, "")

            away_logo_url = f"app/static/{away_logo_file}" if not away_logo_file.startswith("http") else away_logo_file
            home_logo_url = f"app/static/{home_logo_file}" if not home_logo_file.startswith("http") else home_logo_file

            try:
                date_val = pd.to_datetime(row['date'])
                date_str = f"{date_val.strftime('%m/%d')} ({days_of_week[(date_val.weekday()) % 7]})"
            except:
                date_str = f"{row['date']}"

            # 경계선 스타일 (마지막 행은 제외)
            row_border = "border-bottom: 1px solid #EAEAEA;" if idx_count < num_rows - 1 else ""

            # 🌟 [중요] 들여쓰기 공백이나 줄바꿈문자가 들어가면 검은 박스로 쪼개지므로 single-line 구조로 결합합니다.
            row_html = (
                f'<div style="display: flex; align-items: center; width: 100%; padding: 18px 10px; {row_border} min-height: 65px; box-sizing: border-box;">'
                f'<div style="flex: 1.2; text-align: left; color: #666666; font-size: 14px; padding-left: 10px;">{date_str}</div>'
                f'<div style="flex: 0.8; text-align: center; color: #111111; font-size: 14px; font-weight: bold;">{row["time"]}</div>'
                f'<div style="flex: 1.0; text-align: center; color: #666666; font-size: 14px;">{row["stadium"]}</div>'
                f'<div style="flex: 2.0; text-align: right; color: #222222; font-size: 15px; font-weight: bold; padding-right: 15px;">{away_name}</div>'
                f'<div style="flex: 0.4; display: flex; justify-content: center; align-items: center;"><img src="{away_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                f'<div style="flex: 1.0; display: flex; justify-content: center; align-items: center;"><span style="color: #666666; font-size: 12px; font-weight: bold; background: #F4F4F4; border: 1px solid #E2E8F0; padding: 3px 12px; border-radius: 4px; display: inline-block; min-width: 45px; text-align: center;">예정</span></div>'
                f'<div style="flex: 0.4; display: flex; justify-content: center; align-items: center;"><img src="{home_logo_url}" width="24" height="24" style="object-fit: contain;" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'inline\';" /><span style="display:none; font-size:16px;">⚾</span></div>'
                f'<div style="flex: 2.2; text-align: left; color: #222222; font-size: 15px; font-weight: bold; padding-left: 15px; display: flex; align-items: center; gap: 6px;"><span>{home_name}</span><span style="font-size: 10px; color: #999999; border: 1px solid #E0E0E0; border-radius: 3px; padding: 1px 4px; background-color: #FAFAFA; font-weight: normal; line-height: 1.1;">홈</span></div>'
                f'<div style="flex: 1.5;"></div>'
                f'</div>'
            )
            html_rows += row_html

        # 🌟 바깥쪽 대형 화이트 통짜 박스도 들여쓰기 없이 한 번에 결합
        full_table_html = (
            f'<div style="background-color: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 8px; '
            f'box-shadow: 0 1px 4px rgba(0,0,0,0.02); padding: 5px 10px; width: 100%; box-sizing: border-box; '
            f'font-family: -apple-system, BlinkMacSystemFont, \'Malgun Gothic\', sans-serif;">'
            f'{html_rows}'
            f'</div>'
        )

        # 주입 및 렌더링
        st.markdown(full_table_html, unsafe_allow_html=True)

        st.write()

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
