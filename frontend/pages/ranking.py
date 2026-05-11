"""
구단 순위 페이지
- KBO 실시간 순위표
- 구단별 최근 전적
"""

import streamlit as st


def show():
    st.header("🏆 구단 순위")
    st.write("KBO 실시간 순위와 최근 전적을 확인하세요!")

    # TODO: 실제 순위 데이터 크롤링 연동 필요
    st.info("순위 데이터를 불러오는 중입니다...")

    st.subheader("📊 현재 순위")
    # TODO: ranking_chart.py 연동 필요

    st.subheader("📋 최근 경기 결과")
    # TODO: 구단 선택 후 최근 5경기 결과 표시
