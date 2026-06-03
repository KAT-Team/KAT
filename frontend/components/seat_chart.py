"""
좌석 가격 비교 컴포넌트
- 구단별 좌석 등급 및 가격 테이블
"""

import streamlit as st
import pandas as pd
from backend.data.stadium import get_seat_prices


def draw_seat_price_table(team: str):
    prices = get_seat_prices(team)
    if not prices:
        st.info("좌석 가격 정보를 준비 중입니다.")
        return

    rows = []
    for seat, price in prices.items():
        if isinstance(price, tuple):
            if price[0] == price[1]:
                price_str = f"{price[0]:,}원"
            else:
                price_str = f"{price[0]:,}원 ~ {price[1]:,}원"
        else:
            price_str = f"{price:,}원"
        rows.append({"좌석 등급": seat, "가격 (성인 1인)": price_str})

    st.markdown("""
    <style>
    thead tr th { background-color: #4a6fa5 !important; color: white !important; text-align: center !important; }
    tbody tr:nth-child(even) { background-color: #f5f7fa; }
    tbody tr td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
