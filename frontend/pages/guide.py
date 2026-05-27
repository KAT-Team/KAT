"""
직관 도우미 페이지
- 경기장 날씨 예보
- 교통 / 주차 정보
- 직관 체크리스트
- 원정 직관 가이드
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from backend.data.collect import TEAMS, get_ticket_link
from backend.data.stadium import get_stadium_info, get_seat_prices
from backend.data.weather import get_weather, get_weather_comment
from frontend.components.weather_chart import draw_rain_gauge, draw_weather_card
from frontend.components.seat_chart import draw_seat_price_chart
import streamlit.components.v1 as components
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / 'backend' / '.env')
KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY")


def show():
    st.header("🧭 직관 도우미")
    st.write("경기장 날씨, 교통, 준비물 정보를 한 번에 확인하세요!")

    # 구단 및 날짜 선택
    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox(
            "관람할 경기 구단 (홈팀)",
            list(TEAMS.keys()),
            format_func=lambda x: str(TEAMS.get(x, x))
        )
    with col2:
        selected_date = st.date_input(
            "경기 날짜",
            value=datetime.now()
        )

    stadium = get_stadium_info(selected_team)

    if not stadium:
        st.error("경기장 정보를 불러올 수 없습니다.")
        return

    # 경기장 기본 정보
    st.subheader(f"📍 {stadium.get('name', '')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏟️ 수용 인원: {stadium.get('capacity', 0):,}명")
    with col2:
        parking = "✅ 주차 가능" if stadium.get("parking") else "❌ 주차 불가"
        st.info(f"🚗 {parking}")
    with col3:
        ticket_url = get_ticket_link(selected_team)
        st.markdown(f"🎟️ <a href='{ticket_url}' target='_blank'>티켓 예매 바로가기</a>", unsafe_allow_html=True)

    st.divider()

    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌤️ 날씨",
        "🚌 교통/주차",
        "📋 체크리스트",
        "📖 원정 가이드",
        "💺 좌석 가격"
    ])

 # 탭 1: 날씨
    with tab1:
        st.markdown("### 🌤️ 경기 당일 날씨 예보")
        date_str = selected_date.strftime("%Y%m%d")
        weather = get_weather(selected_team, date_str)

        # === 1. 메인 영역: 게이지 + 직관 추천 ===
        rain_prob = weather.get("rain_prob", 0)
        col_gauge, col_recommend = st.columns([1, 1.3])

        with col_gauge:
            fig = draw_rain_gauge(rain_prob)
            st.plotly_chart(fig, use_container_width=True)

        with col_recommend:
            st.markdown("#### 🎯 직관 추천")
            comment = get_weather_comment(rain_prob)
            if rain_prob >= 70:
                st.error(f"### 🌧️ {comment}")
            elif rain_prob >= 40:
                st.warning(f"### ⛅ {comment}")
            else:
                st.success(f"### ☀️ {comment}")

            st.markdown("**📌 날씨별 준비물**")
            if rain_prob >= 40:
                items = ["🌂 우산 필수", "🧥 방수 재킷", "👟 방수 신발"]
            else:
                items = ["🕶️ 선글라스", "🧴 선크림", "🧢 모자"]

            # 칩(chip) 형태로 가로 배치
            chips_html = " ".join([
                f'<span style="display: inline-block; background: #F5F6FA; '
                f'border: 1px solid #E8EAF1; border-radius: 20px; '
                f'padding: 8px 16px; margin: 4px 4px 4px 0; font-size: 14px; '
                f'color: #2C3144; font-weight: 500;">{item}</span>'
                for item in items
            ])
            st.markdown(chips_html, unsafe_allow_html=True)

        st.divider()

        # === 2. 상세 날씨 정보 카드 ===
        st.markdown("#### 📊 상세 날씨 정보")
        draw_weather_card(weather)

        # === 3. 디버그 정보 (개발용) ===
        st.write("--- API 연동 데이터 확인용 ---")
        st.write(weather)

    # 탭 2: 교통/주차
    with tab2:
        st.write("### 교통 및 주차 정보")
        st.write(f"📍 주소: {stadium.get('address', '')}")

        # 카카오맵 지도 임베드
        lat = stadium.get('lat', 37.5)
        lng = stadium.get('lng', 127.0)
        stadium_name = stadium.get('name', '')

        if KAKAO_MAP_API_KEY:
            map_html = f"""
            <div id="map" style="width:100%;height:400px;border-radius:10px;"></div>
            <script type="text/javascript"
                src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_MAP_API_KEY}">
            </script>
            <script>
                var container = document.getElementById('map');
                var options = {{
                    center: new kakao.maps.LatLng({lat}, {lng}),
                    level: 4
                }};
                var map = new kakao.maps.Map(container, options);
                var markerPosition = new kakao.maps.LatLng({lat}, {lng});
                var marker = new kakao.maps.Marker({{position: markerPosition}});
                marker.setMap(map);
                var infowindow = new kakao.maps.InfoWindow({{
                    content: '<div style="padding:5px;">{stadium_name}</div>'
                }});
                infowindow.open(map, marker);
            </script>
            """
            components.html(map_html, height=420)
        else:
            st.info(f"📍 {stadium_name}\n\n주소: {stadium.get('address', '')}")

        st.divider()

        parking = stadium.get("parking")
        if parking:
            st.success("✅ 경기장 주차 가능")
            st.write("- 경기 시작 2시간 전부터 입차 가능")
            st.write("- 경기 종료 후 혼잡 예상, 대중교통 이용 권장")
        else:
            st.error("❌ 경기장 주차 불가 — 대중교통 이용 권장")

    # 탭 3: 체크리스트
    with tab3:
        st.write("### ✅ 직관 체크리스트")

        rain_prob = weather.get("rain_prob", 0) if 'weather' in dir() else 0

        st.write("#### 기본 준비물")
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("🎟️ 티켓 (모바일 or 실물)")
            st.checkbox("🪪 신분증")
            st.checkbox("👟 편한 신발")
            st.checkbox("💰 현금/카드")
        with col2:
            st.checkbox("📱 스마트폰 충전")
            st.checkbox("🎽 응원 도구")
            st.checkbox("🍱 간식 / 음료")
            st.checkbox("🧴 선크림")

        if rain_prob >= 40:
            st.write("#### ☔ 우천 대비 준비물")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("🌂 우산")
                st.checkbox("🧥 방수 재킷")
            with col2:
                st.checkbox("👟 방수 신발")
                st.checkbox("🛡️ 우비")

        st.divider()
        st.write("#### 📱 유용한 앱")
        st.write("- **KBO 공식 앱**: 실시간 경기 정보")
        st.write("- **카카오맵**: 경기장 길 찾기")
        st.write("- **기상청 날씨**: 실시간 날씨 확인")

    # 탭 4: 원정 가이드
    with tab4:
        st.write("### 📖 원정 직관 가이드")

        home_section = stadium.get('home_section', '1루 내야/외야')
        away_section = stadium.get('away_section', '3루 내야/외야')
        st.info(f"🏠 홈팀 응원석: **{home_section}**")
        st.info(f"✈️ 원정팀 응원석: **{away_section}**")

        st.write("#### 응원 규칙")
        st.write("- 원정석에서는 홈팀 응원 금지")
        st.write("- 상대 팀 비하 발언 및 행동 금지")
        st.write("- 홈팀 선수 야유 자제")

        st.write("#### 반입 금지 물품")
        st.write("- 🚫 캔/유리병 음료")
        st.write("- 🚫 외부 음식 (일부 구장)")
        st.write("- 🚫 긴 막대 응원 도구 (2m 이상)")
        st.write("- 🚫 위험물 (화기류 등)")

        st.write("#### 경기장 편의시설")
        capacity = stadium.get('capacity', 0)
        st.write(f"- 수용 인원: {capacity:,}명")
        st.write("- 화장실: 각 층마다 위치")
        st.write("- 매점: 내야 및 외야 구역 배치")
        st.write("- 수유실: 1층 안내데스크 문의")

    # 탭 5: 좌석 가격
    with tab5:
        st.write("### 💺 좌석 등급별 가격")
        prices = get_seat_prices(selected_team)

        if prices:
            fig = draw_seat_price_chart(selected_team)
            st.plotly_chart(fig, use_container_width=True)

            st.write("#### 좌석 가격표")
            for seat, price in prices.items():
                st.write(f"- **{seat}**: {price:,}원")
        else:
            st.info("좌석 가격 정보를 준비 중입니다.")

        st.divider()
        ticket_url = get_ticket_link(selected_team)
        team_name = TEAMS.get(selected_team, selected_team)
        st.markdown(f"### 🎟️ <a href='{ticket_url}' target='_blank'>{team_name} 티켓 예매 바로가기</a>", unsafe_allow_html=True)
