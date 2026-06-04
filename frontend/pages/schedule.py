"""
경기 일정 캘린더 페이지
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from backend.data.collect import TEAMS, get_ticket_link
from backend.data.preprocess import preprocess_schedule, filter_by_team
from frontend.components.calendar_view import draw_schedule_table, draw_monthly_chart
import json
import os


def show():
    # 1. 화면을 좌우 여백과 중앙 콘텐츠 영역으로 분할 (비율: 여백 1.5, 본문 7, 여백 1.5)
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    with center_content:
        st.header("📅 경기 일정")
        st.write("KBO 10개 구단의 경기 일정을 한눈에 확인하세요!")

        # 필터
        col1, col2 = st.columns(2)
        with col1:
            selected_team = st.selectbox(
                "구단 선택",
                ["전체"] + list(TEAMS.keys()),
                format_func=lambda x: "전체 구단" if x == "전체" else str(TEAMS.get(x, x))
            )
        with col2:
            now = datetime.now()
            selected_month = st.selectbox(
                "월 선택",
                list(range(3, 11)),
                index=now.month - 3 if 3 <= now.month <= 10 else 0,
                format_func=lambda x: f"{x}월"
            )

        try:
            # 1. JSON 파일 로드
            json_path = os.path.join(os.getcwd(), "kbo_schedule.json")
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # 2. DataFrame 변환
            df_all = pd.DataFrame(raw_data)

            # 3. 월 필터링
            month_prefix = f"{selected_month}월"
            df = df_all[df_all["날짜"].str.startswith(month_prefix)].copy()

            # 4. 컬럼명 변환 (rename 먼저!)
            df = df.rename(columns={
                "날짜": "date",
                "시간": "time",
                "경기": "play",
                "구장": "stadium"
            })

            # 5. play 컬럼에서 away_team, home_team 분리
            df['away_team'] = df['play'].str.split(' vs ').str[0].str.strip()
            df['home_team'] = df['play'].str.split(' vs ').str[1].str.strip()

            # 6. 한글 팀명 → 영어 코드 변환
            TEAM_NAME_KR = {
                "기아": "KIA",
                "삼성": "Samsung",
                "LG": "LG",
                "두산": "Doosan",
                "KT": "KT",
                "SSG": "SSG",
                "롯데": "Lotte",
                "한화": "Hanwha",
                "NC": "NC",
                "키움": "Kiwoom"
            }
            df['away_team'] = df['away_team'].map(
                lambda x: TEAM_NAME_KR.get(str(x), str(x)) if pd.notna(x) else x
            )
            df['home_team'] = df['home_team'].map(
                lambda x: TEAM_NAME_KR.get(str(x), str(x)) if pd.notna(x) else x
            )

            # 7. 날짜 형식 변환 "5월 05.01(금)" → "2026-05-01"
            def fix_date_format(row_date):
                try:
                    pure_date = row_date.split(" ")[1].split("(")[0]
                    month, day = pure_date.split(".")
                    return f"2026-{month}-{day}"
                except:
                    return row_date

            df['date'] = df['date'].apply(fix_date_format)

        except Exception as e:
            st.error(f"데이터 파일을 읽어오는 중 오류가 발생했습니다: {e}")
            st.warning("최상위 폴더에 kbo_schedule.json 파일이 존재하는지 확인해 주세요.")
            return

        if df.empty:
            st.warning(f"{selected_month}월의 경기 일정이 없습니다.")
            return

        # 8. 전처리
        df = preprocess_schedule(df)

        # 9. 구단 필터링
        if selected_team != "전체":
            df = filter_by_team(df, selected_team)

        # 10. 월별 경기 수 차트
        with st.expander("📊 일별 경기 수 보기", expanded=False):
            fig = draw_monthly_chart(df)
            st.plotly_chart(fig, use_container_width=True)

        # 11. 예매 링크
        if selected_team != "전체":
            ticket_url = get_ticket_link(selected_team)
            team_name = TEAMS.get(selected_team, selected_team)
            st.markdown(
                f"### 🎟️ [{team_name} 티켓 예매 바로가기]({ticket_url})",
                unsafe_allow_html=False
            )
            st.divider()

        # 12. 경기 일정 표시
        st.subheader(f"{selected_month}월 경기 일정 ({len(df)}경기)")
        draw_schedule_table(df)
