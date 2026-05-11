"""
구단 순위 페이지
- KBO 순위표
- 구단별 승률 차트
- 최근 전적
"""

import streamlit as st
from frontend.components.ranking_chart import (
    get_ranking_data,
    draw_ranking_table,
    draw_win_rate_chart
)
from backend.data.collect import TEAMS


def show():
    st.header("🏆 구단 순위")
    st.write("KBO 현재 순위와 팀별 성적을 확인하세요!")

    # 순위 데이터
    ranking_df = get_ranking_data()

    # 탭 구성
    tab1, tab2 = st.tabs(["📊 순위표", "📈 승률 비교"])

    with tab1:
        fig = draw_ranking_table(ranking_df)
        st.plotly_chart(fig, use_container_width=True)

        # 1~3위 하이라이트
        st.write("#### 🏅 상위 3팀")
        col1, col2, col3 = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        for i, (col, medal) in enumerate(zip([col1, col2, col3], medals)):
            row = ranking_df.iloc[i]
            team_name = TEAMS.get(row['team'], row['team'])
            with col:
                st.metric(
                    f"{medal} {i+1}위",
                    team_name,
                    f"승률 {row['win_rate']:.3f}"
                )

    with tab2:
        fig = draw_win_rate_chart(ranking_df)
        st.plotly_chart(fig, use_container_width=True)

        st.write("#### 📋 상세 성적")
        display_df = ranking_df.copy()
        display_df['team'] = display_df['team'].map(
            lambda x: str(TEAMS.get(x, x))
        )
        display_df.columns = ['순위', '팀', '승', '패', '무', '승률']
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
