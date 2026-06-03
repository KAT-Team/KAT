"""
구단 순위 페이지
- KBO 실시간 순위표 (크롤링 데이터 연동)
- 팀 고유 색상 적용
"""

import os
import pandas as pd
import streamlit as st
from backend.data.collect import TEAMS
from backend.data.team_crawler import crawl_all_team_stats

# 구단별 고유 색상
TEAM_COLORS = {
    "KIA": "#EA0029",  # 기아 빨강
    "Samsung": "#074CA1",  # 삼성 파랑
    "LG": "#C30452",  # LG 빨강
    "Doosan": "#131230",  # 두산 네이비
    "KT": "#000000",  # KT 검정
    "SSG": "#CE0E2D",  # SSG 빨강
    "Lotte": "#002058",  # 롯데 네이비
    "Hanwha": "#FF6600",  # 한화 주황
    "NC": "#071D49",  # NC 네이비
    "Kiwoom": "#820024",  # 키움 와인
}


# 로컬 SVG 파일의 내용을 텍스트로 읽어 HTML에 직접 삽입 가능한 구조로 반환하는 함수
def get_inline_svg(team_key):
    # 파일명이 'logo_doosan.svg' 처럼 소문자 기반으로 매핑된다고 가정합니다.
    # team_key가 대소문자가 섞여있으므로 .lower()를 적용합니다.
    file_name = f"logo_{team_key.lower()}.svg"

    # KAT 폴더 내에서 실행될 때의 상대 경로 지정
    file_path = os.path.join("frontend", "assets", file_name)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
                # SVG 태그 내부 스타일이 깨지지 않도록 크기 강제 지정을 위한 래핑 박스 처리
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
        rows.append(
            {
                "rank": data.get("rank", 0),
                "team": team,
                "win": data.get("win", 0),
                "lose": data.get("lose", 0),
                "draw": data.get("draw", 0),
                "game": data.get("win", 0) + data.get("lose", 0) + data.get("draw", 0),
                "win_rate": data.get("win_rate", 0.0),
                "recent_10": data.get("recent_10", ""),
                "streak": data.get("streak", ""),
                "avg": data.get("avg", 0.0),
                "era": data.get("era", 0.0),
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

    # 전체 순위표
    # 1. 화면을 좌우 여백과 중앙 콘텐츠 영역으로 분할 (비율: 여백 1.5, 본문 7, 여백 1.5)
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    # 2. 중앙 콘텐츠 영역 내부에서만 순위표 빌드
    with center_content:
        # 게임차 계산을 위한 1위 팀 기준 데이터 추출
        leader_row = ranking_df.iloc[0]
        leader_win = int(leader_row["win"])
        leader_lose = int(leader_row["lose"])

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
<div style="width: 9.0%; display: flex; align-items: center; justify-content: center;">PS 진출 확률</div>
</div>"""

        # 10개 구단 데이터 반복 돌며 카드 쌓기
        for _, row in ranking_df.iterrows():
            team_key = str(row["team"])
            team_name = str(TEAMS.get(team_key, team_key))
            rank = int(row["rank"])
            color = TEAM_COLORS.get(team_key, "#333333")

            # [변경 포인트] 로컬에서 SVG 코드를 직접 읽어와 임베딩할 준비
            logo_svg = get_inline_svg(team_key)

            # 개인 게임차 계산
            current_win = int(row["win"])
            current_lose = int(row["lose"])
            gap = ((leader_win - current_win) + (current_lose - leader_lose)) / 2
            gap_str = "0" if gap == 0 else f"{gap:.1f}"

            # 연승/연패에 따른 다이내믹 컬러 정의
            streak_val = str(row["streak"])
            streak_color = (
                "#1e40af"
                if "승" in streak_val
                else "#b91c1c" if "패" in streak_val else "#333333"
            )

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
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">{row['avg']:.3f}</div>
<div style="width: 6.5%; display: flex; align-items: center; justify-content: center;">{row['era']:.2f}</div>
<div style="width: 9.0%; display: flex; align-items: center; justify-content: center; color: {color}; font-weight: bold;">{row['win_rate']:.3f}</div>
</div>"""

        # 전체 하얀 박스 닫기 및 렌더링
        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)

    st.divider()
