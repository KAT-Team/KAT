"""
구단 순위 페이지
- KBO 실시간 순위표 (크롤링 데이터 연동)
- 팀 고유 색상 적용 및 가을야구 진출 확률 시각화
"""

import os
import math
import pandas as pd
import streamlit as st
from backend.data.collect import TEAMS
from backend.data.team_crawler import crawl_all_team_stats

# 구단별 고유 색상
TEAM_COLORS = {
    "KIA": "#EA0029",     # 기아 빨강
    "Samsung": "#074CA1", # 삼성 파랑
    "LG": "#C30452",      # LG 빨강
    "Doosan": "#131230",   # 두산 네이비
    "KT": "#000000",      # KT 검정
    "SSG": "#CE0E2D",     # SSG 빨강
    "Lotte": "#002058",   # 롯데 네이비
    "Hanwha": "#FF6600",  # 한화 주황
    "NC": "#071D49",      # NC 네이비
    "Kiwoom": "#820024",  # 키움 와인
}

TEAM_NAME_KR = {
    "기아": "KIA", "삼성": "Samsung", "LG": "LG", "두산": "Doosan", "KT": "KT",
    "SSG": "SSG", "롯데": "Lotte", "한화": "Hanwha", "NC": "NC", "키움": "Kiwoom"
}

TEAM_NAME_DISPLAY = {
    "KIA": "KIA", "Samsung": "삼성", "LG": "LG", "Doosan": "두산", "KT": "KT",
    "SSG": "SSG", "Lotte": "롯데", "Hanwha": "한화", "NC": "NC", "Kiwoom": "키움",
}

# 로컬 SVG 파일의 내용을 텍스트로 읽어 HTML에 직접 삽입 가능한 구조로 반환하는 함수
def get_inline_svg(team_key):
    file_name = f"logo_{team_key.lower()}.svg"
    file_path = os.path.join("frontend", "assets", file_name)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
                return f'<div style="width: 24px; height: 24px; margin-right: 8px; display: flex; align-items: center; justify-content: center;">{svg_content}</div>'
        except Exception:
            return ""
    return ""


@st.cache_data(ttl=3600)
def load_ranking_data() -> pd.DataFrame:
    stats = crawl_all_team_stats()
    if not stats:
        return pd.DataFrame()

    rows = []
    for team, data in stats.items():
        # 기본 변수 추출
        rbi = data.get("team_rbi", 0)
        r = data.get("team_r", 0)
        win = data.get("win", 0)
        lose = data.get("lose", 0)
        draw = data.get("draw", 0)
        current_win_rate = data.get("win_rate", 0.0)

        # 1. 피타고리안 승률 계산
        pytagorean = round((rbi ** 1.83) / ((rbi ** 1.83) + (r ** 1.83)), 3) if (rbi + r) > 0 else 0.0

        # 2. 가을야구 진출 확률 계산 (기대 최종 승수 기반)
        total_games = 144
        remained_games = total_games - (win + lose + draw)

        # 미래 기대 승률 (피타고리안과 현재 승률의 평균 시너지 반영)
        expected_future_win_rate = (pytagorean + current_win_rate) / 2
        # 최종 예상 승수
        expected_final_wins = win + (remained_games * expected_future_win_rate)

        # 시그모이드 함수를 이용한 최종 가을야구 진출 확률
        ps_probability = 1 / (1 + math.exp(-(expected_final_wins - 70.8) * 0.185))
        postseason_pct = round(ps_probability * 100, 1)

        rows.append(
            {
                "rank": data.get("rank", 0),
                "team": team,
                "win": win,
                "lose": lose,
                "draw": draw,
                "game": win + lose + draw,
                "win_rate": current_win_rate,
                "recent_10": data.get("recent_10", ""),
                "streak": data.get("streak", ""),
                "avg": data.get("avg", 0.0),
                "era": data.get("era", 0.0),
                "team_r": data.get("team_r", 0),
                "team_rbi": data.get("team_rbi", 0),
                "pytagorean": pytagorean,
                "postseason_prob": postseason_pct  # 보정된 확률 적재
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values("rank").reset_index(drop=True)
    return df


def show():
    st.markdown(
        """
    <style>
    h1 a, h2 a, h3 a, h4 a { display: none !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.spinner("순위 데이터 불러오는 중..."):
        ranking_df = load_ranking_data()

    if ranking_df.empty:
        st.error("순위 데이터를 불러올 수 없습니다.")
        return

    # 화면 분할
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    with center_content:
        # 상위 5팀 하이라이트
        st.write("#### 🍂 포스트시즌 진출 예상 상위 5팀")
        cols = st.columns(5)
        labels = ["1위", "2위", "3위", "4위", "5위"]

        for i, (col, label) in enumerate(zip(cols, labels)):
            row = ranking_df.iloc[i]
            raw_team_name = str(row["team"])
            team_key = TEAM_NAME_KR.get(raw_team_name, raw_team_name)
            team_name = str(TEAMS.get(str(row["team"]), str(row["team"])))
            color = TEAM_COLORS.get(str(row["team"]), "#333333")
            border_style = "solid"

            logo_svg = get_inline_svg(team_key)
            if logo_svg:
                logo_svg = logo_svg.replace("width: 24px; height: 24px;", "width: 80px; height: 80px;")
                logo_svg = logo_svg.replace("margin-right: 8px;", "margin-bottom: 8px;")

            with col:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(160deg, {color}22, {color}08);
                    border: 2px {border_style} {color};
                    border-radius: 12px;
                    padding: 16px 12px;
                    text-align: center;
                    position: relative;
                ">
                    <div style="font-size: 26px; font-weight: 900; color: {color};
                                font-family: 'Georgia', serif;">{label}</div>
                    <div style="display: flex; align-items: center; justify-content: center; margin: 8px 0; min-height: 24px;">
                        {logo_svg}
                    </div>
                    <div style="
                        background: {color};
                        color: white;
                        border-radius: 6px;
                        padding: 4px 8px;
                        font-size: 15px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 4px 0;
                    ">{row['win_rate']:.3f}</div>
                    <div style="font-size: 12px; color: #888; margin-top: 4px;">
                        ⚾ {row['win']}승 {row['lose']}패 {row['draw']}무
                    </div>
                    <div style="font-size: 14px; font-weight: bold; color: {color}; margin: 6px 0 2px 0;">
                        PS 진출 확률: {row['postseason_prob']:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.write("#### 📊 전체 순위")

        leader_row = ranking_df.iloc[0]
        leader_win = int(leader_row["win"])
        leader_lose = int(leader_row["lose"])

        max_avg = ranking_df["avg"].max()
        min_avg = ranking_df["avg"].min()
        max_era = ranking_df["era"].max()
        min_era = ranking_df["era"].min()

        html_content = f"""<div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); margin-bottom: 20px;">
<div style="padding: 0px 16px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; font-weight: bold; font-size: 15px; color: #222222; height: 36px; border-bottom: 1px solid #F3F4F6; padding-bottom: 12px;">
<div style="width: 4.1%; display: flex; align-items: center; justify-content: flex-start;">순위</div>
<div style="width: 20.8%; display: flex; align-items: center; justify-content: flex-start; padding-left: 8px;"></div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">승률</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">경기</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">승</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">패</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">무</div>
<div style="width: 6.0%; display: flex; align-items: center; justify-content: center;">게임차</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">연속</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">타율</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">ERA</div>
<div style="width: 10.0%; display: flex; align-items: center; justify-content: center;">PS 진출 확률</div>
</div>"""

        for _, row in ranking_df.iterrows():
            raw_team_name = str(row["team"])
            team_key = TEAM_NAME_KR.get(raw_team_name, raw_team_name)
            team_name = TEAM_NAME_DISPLAY.get(team_key, raw_team_name)
            rank = int(row["rank"])
            color = TEAM_COLORS.get(team_key, "#333333")
            logo_svg = get_inline_svg(team_key)

            gap = ((leader_win - int(row["win"])) + (int(row["lose"]) - leader_lose)) / 2
            gap_str = "0" if gap == 0 else f"{gap:.1f}"

            streak_val = str(row["streak"])
            streak_color = "#1e40af" if "승" in streak_val else "#b91c1c" if "패" in streak_val else "#333333"

            current_avg = row["avg"]
            if current_avg == max_avg:
                avg_color = "#1e40af; font-weight: bold;"
            elif current_avg == min_avg:
                avg_color = "#b91c1c; font-weight: bold;"
            else:
                avg_color = "#333333;"

            current_era = row["era"]
            if current_era == min_era:
                era_color = "#1e40af; font-weight: bold;"
            elif current_era == max_era:
                era_color = "#b91c1c; font-weight: bold;"
            else:
                era_color = "#333333;"

            # 보정된 유연한 확률 변수가 퍼센트로 바인딩됩니다.
            html_content += f"""<div style="background-color: {color}0D; border-left: 5px solid {color}; border-top: 1px solid {color}1A; border-right: 1px solid {color}1A; border-bottom: 1px solid {color}1A; border-radius: 8px; padding: 10px 16px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; font-size: 16px; font-weight: 500; color: #333333;">
<div style="width: 4.1%; display: flex; align-items: center; justify-content: flex-start; font-size: 18px; font-weight: 800; color: {color};">{rank}</div>
<div style="width: 20.8%; display: flex; align-items: center; justify-content: flex-start; padding-left: 8px;">
{logo_svg}<span style="color: {color}; font-weight: bold; font-size: 16px;">{team_name}</span>
</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center; color: {color}; font-weight: bold;">{row['win_rate']:.3f}</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">{row['game']}</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">{row['win']}</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">{row['lose']}</div>
<div style="width: 5.5%; display: flex; align-items: center; justify-content: center;">{row['draw']}</div>
<div style="width: 6.0%; display: flex; align-items: center; justify-content: center;">{gap_str}</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center; color: {streak_color}; font-weight: bold;">{streak_val}</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center; color: {avg_color}">{row['avg']:.3f}</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center; color: {era_color}">{row['era']:.2f}</div>
<div style="width: 10.0%; display: flex; align-items: center; justify-content: center; color: {color}; font-weight: bold;">{row['postseason_prob']:.1f}%</div>
</div>"""

        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)

    st.divider()
