"""
좌석 가격 비교 컴포넌트
- 구단별 좌석 등급 및 가격 (표 + 데이터 바)
"""

import streamlit as st
from backend.data.stadium import get_seat_prices


def draw_seat_price_table(team: str):
    prices = get_seat_prices(team)
    if not prices:
        st.info("좌석 가격 정보를 준비 중입니다.")
        return

    def hi_of(p):
        return p[1] if isinstance(p, tuple) else p

    items = sorted(prices.items(), key=lambda kv: hi_of(kv[1]), reverse=True)
    max_price = max(hi_of(p) for p in prices.values())

    rows_html = ""
    for seat, price in items:
        if isinstance(price, tuple):
            lo, hi = price
            price_str = f"{lo:,} ~ {hi:,}원" if lo != hi else f"{lo:,}원"
        else:
            hi = price
            price_str = f"{price:,}원"
        pct = hi / max_price * 100
        rows_html += (
            '<div style="display:flex; align-items:center; padding:10px 16px; '
            'border-bottom:1px solid #EEF0F4;">'
            f'<div style="flex:0 0 36%; font-weight:600; color:#2C3144; font-size:14px;">{seat}</div>'
            f'<div style="flex:0 0 30%; color:#5a6488; font-weight:700; font-size:13px;">{price_str}</div>'
            '<div style="flex:1; background:#F0F2F6; border-radius:6px; height:10px; overflow:hidden;">'
            f'<div style="width:{pct:.0f}%; height:100%; '
            'background:linear-gradient(90deg,#7A86B6,#5a6488);"></div></div>'
            '</div>'
        )

    html = (
        '<div style="background:#fff; border:1px solid #E8EAF1; border-radius:14px; '
        'overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
        '<div style="display:flex; padding:12px 16px; background:#3f4a73; color:#fff; '
        'font-weight:700; font-size:13px;">'
        '<div style="flex:0 0 36%;">좌석 등급</div>'
        '<div style="flex:0 0 30%;">가격 (성인 1인)</div>'
        '<div style="flex:1;">상대 가격</div></div>'
        f'{rows_html}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
