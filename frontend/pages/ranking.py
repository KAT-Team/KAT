"""
구단 순위 페이지
- KBO 실시간 순위표 (크롤링 데이터 연동)
- 팀 고유 색상 적용
"""

import streamlit as st
import pandas as pd
from backend.data.team_crawler import crawl_all_team_stats
from backend.data.collect import TEAMS

# 구단별 고유 색상
TEAM_COLORS = {
    "KIA":     "#EA0029",  # 기아 빨강
    "Samsung": "#074CA1",  # 삼성 파랑
    "LG":      "#C30452",  # LG 빨강
    "Doosan":  "#131230",  # 두산 네이비
    "KT":      "#000000",  # KT 검정
    "SSG":     "#CE0E2D",  # SSG 빨강
    "Lotte":   "#002058",  # 롯데 네이비
    "Hanwha":  "#FF6600",  # 한화 주황
    "NC":      "#071D49",  # NC 네이비
    "Kiwoom":  "#820024",  # 키움 와인
}


@st.cache_data(ttl=3600)
def load_ranking_data() -> pd.DataFrame:
    stats = crawl_all_team_stats()
    if not stats:
        return pd.DataFrame()

    rows = []
    for team, data in stats.items():
        rows.append({
            "rank":      data.get("rank", 0),
            "team":      team,
            "win":       data.get("win", 0),
            "lose":      data.get("lose", 0),
            "draw":      data.get("draw", 0),
            "win_rate":  data.get("win_rate", 0.0),
            "recent_10": data.get("recent_10", ""),
            "streak":    data.get("streak", ""),
            "avg":       data.get("avg", 0.0),
            "era":       data.get("era", 0.0),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("rank").reset_index(drop=True)
    return df


def show():
    st.markdown("""
    <style>
    h1 a, h2 a, h3 a, h4 a { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.header("🏆 구단 순위")
    st.write("KBO 현재 순위와 팀별 성적을 확인하세요!")

    with st.spinner("순위 데이터 불러오는 중..."):
        ranking_df = load_ranking_data()

    if ranking_df.empty:
        st.error("순위 데이터를 불러올 수 없습니다.")
        return

    # 상위 3팀 하이라이트
    st.write("#### 🏅 상위 3팀")
    col1, col2, col3 = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]

    for i, (col, medal) in enumerate(zip([col1, col2, col3], medals)):
        row = ranking_df.iloc[i]
        team_name = str(TEAMS.get(str(row["team"]), str(row["team"])))
        color = TEAM_COLORS.get(str(row["team"]), "#333333")
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}22, {color}11);
                border: 2px solid {color};
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            ">
                <div style="font-size: 32px;">{medal}</div>
                <div style="font-size: 20px; font-weight: bold; margin: 8px 0; color: {color};">{team_name}</div>
                <div style="font-size: 14px; color: #666;">승률 {row['win_rate']:.3f}</div>
                <div style="font-size: 13px; color: #888;">{row['win']}승 {row['lose']}패 {row['draw']}무</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 전체 순위표
    st.write("#### 📊 전체 순위")
    for _, row in ranking_df.iterrows():
        team_name = str(TEAMS.get(str(row["team"]), str(row["team"])))
        rank = int(row["rank"])
        color = TEAM_COLORS.get(str(row["team"]), "#333333")

        st.markdown(f"""
        <div style="
            background: {color}0d;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 12px 20px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        ">
            <span style="font-size: 18px; font-weight: bold; width: 40px; color: {color};">{rank}</span>
            <span style="font-size: 16px; font-weight: bold; flex: 1; color: #222;">{team_name}</span>
            <span style="font-size: 14px; color: #555; margin-right: 20px;">{row['win']}승 {row['lose']}패 {row['draw']}무</span>
            <span style="font-size: 15px; font-weight: bold; color: {color}; width: 60px; text-align: right;">
                {row['win_rate']:.3f}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 상세 성적
    st.write("#### 📋 상세 성적")
    display_df = ranking_df.copy()
    display_df["team"] = display_df["team"].map(
        lambda x: str(TEAMS.get(str(x), str(x)))
    )
    display_df = display_df.rename(columns={
        "rank": "순위", "team": "팀", "win": "승", "lose": "패",
        "draw": "무", "win_rate": "승률", "avg": "타율", "era": "ERA",
        "recent_10": "최근10경기", "streak": "연속"
    })
    st.dataframe(
        display_df[["순위", "팀", "승", "패", "무", "승률", "타율", "ERA", "최근10경기", "연속"]],
        use_container_width=True,
        hide_index=True
    )
