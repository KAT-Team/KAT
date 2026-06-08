"""
직관 도우미 페이지
- 경기장 날씨 예보
- 교통 / 주차 정보
- 직관 체크리스트
- 원정 직관 가이드
"""

import streamlit as st
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from backend.data.collect import TEAMS, get_ticket_link
from backend.data.stadium import get_stadium_info, get_seat_prices
from backend.data.weather import get_weather, get_weather_comment
from frontend.components.weather_chart import draw_weather_card
from frontend.components.seat_chart import draw_seat_price_table
import streamlit.components.v1 as components
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / 'backend' / '.env')
KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY")


def get_nearby_parking(lat, lng, radius=1000):
    """카카오 로컬 REST API로 주변 주차장(PK6) 검색."""
    if not KAKAO_REST_KEY:
        return []
    try:
        res = requests.get(
            "https://dapi.kakao.com/v2/local/search/category.json",
            headers={"Authorization": f"KakaoAK {KAKAO_REST_KEY}"},
            params={
                "category_group_code": "PK6",
                "x": lng, "y": lat,
                "radius": radius, "sort": "distance", "size": 15,
            },
            timeout=5,
        )
        res.raise_for_status()
        return res.json().get("documents", [])
    except Exception:
        return []


def show():
    # 1. 화면을 좌우 여백과 중앙 콘텐츠 영역으로 분할 (비율: 여백 1.5, 본문 7, 여백 1.5)
    left_space, center_content, right_space = st.columns([1.5, 7.0, 1.5])

    with center_content:
        st.markdown("""
        <style>
        h1 a, h2 a, h3 a, h4 a { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

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
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-height: 68px;
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 8px 16px;
        ">
            <a href='{ticket_url}' target='_blank' style="
                color: #E8A020 !important;
                font-size: 18px;
                font-weight: 700;
                text-decoration: underline;
                text-underline-offset: 3px;
            ">
                🎟️ 티켓 예매 바로가기
            </a>
        </div>
        """, unsafe_allow_html=True)

        # 탭 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🌤️ 날씨",
            "🚌 교통/주차",
            "🎒 추천 준비물",
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
                st.markdown(f"""
                <div style="
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 200px;
                ">
                    <div style="font-size: 80px; font-weight: bold; color: #1f4e79;">{rain_prob}%</div>
                    <div style="color: #888; font-size: 15px; margin-top: 8px;">강수 확률</div>
                </div>
                """, unsafe_allow_html=True)

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
                    items = ["🌂 우산", "🧥 우비"]
                else:
                    items = ["🧴 선크림", "🧢 모자", "🌀 손선풍기"]

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

        # 탭 2: 교통/주차
        with tab2:
            st.write("### 교통 및 주차 정보")
            st.write(f"📍 주소: {stadium.get('address', '')}")

            lat = stadium.get('lat', 37.5)
            lng = stadium.get('lng', 127.0)
            stadium_name = stadium.get('name', '')

            # 파이썬(REST)에서 주차장 검색 → iframe 문제 우회
            parking_list = get_nearby_parking(lat, lng, 1000)
            parking_js = json.dumps(
                [{"name": p["place_name"], "x": p["x"], "y": p["y"]} for p in parking_list],
                ensure_ascii=False,
            )

            if KAKAO_MAP_API_KEY:
                map_html = f"""
                <div id="map" style="width:100%;height:400px;border-radius:10px;"></div>
                <script type="text/javascript"
                    src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_MAP_API_KEY}&autoload=false">
                </script>
                <script>
                    kakao.maps.load(function () {{
                        var center = new kakao.maps.LatLng({lat}, {lng});
                        var map = new kakao.maps.Map(
                            document.getElementById('map'),
                            {{ center: center, level: 5 }}
                        );

                        // 줌 +/- 버튼
                        var zoomControl = new kakao.maps.ZoomControl();
                        map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

                        // 경기장 마커
                        var marker = new kakao.maps.Marker({{ position: center }});
                        marker.setMap(map);
                        var infowindow = new kakao.maps.InfoWindow({{
                            content: '<div style="padding:5px;">{stadium_name}</div>'
                        }});
                        infowindow.open(map, marker);

                        // 주차장 마커 (파이썬에서 받은 목록)
                        var parking = {parking_js};
                        var bounds = new kakao.maps.LatLngBounds();
                        bounds.extend(center);
                        parking.forEach(function (p) {{
                            var pos = new kakao.maps.LatLng(p.y, p.x);
                            bounds.extend(pos);
                            var pkMarker = new kakao.maps.Marker({{ position: pos, map: map }});
                            var iw = new kakao.maps.InfoWindow({{
                                content: '<div style="padding:5px;font-size:12px;">P ' + p.name + '</div>'
                            }});
                            kakao.maps.event.addListener(pkMarker, 'click', function () {{
                                iw.open(map, pkMarker);
                            }});
                        }});
                        if (parking.length > 0) map.setBounds(bounds);
                    }});
                </script>
                """
                components.html(map_html, height=420)

                # ── 경기장 자체 주차 정보 ──
                st.divider()
                stadium_name = stadium.get("name", "")
                if selected_team == "Kiwoom" or "고척" in stadium_name:
                    st.warning("⚠️ 경기장 주차장은 **관계자 전용**으로 일반 관람객은 이용할 수 없습니다. "
                               "주변 주차장이나 대중교통을 이용하세요.")
                elif stadium.get("parking"):
                    st.success("✅ 경기장 주차 가능")
                    st.write("- 경기 시작 2시간 전부터 입차 가능")
                    st.write("- 경기 종료 후 혼잡 예상, 대중교통 이용 권장")
                else:
                    st.error("❌ 경기장 주차 불가 — 대중교통 이용 권장")

                # ── 주변 주차장 목록 ──
                st.divider()
                st.markdown("##### 🅿️ 주변 주차장 (반경 1km)")
                if parking_list:
                    for p in parking_list:
                        dist = p.get("distance", "")
                        addr = p.get("road_address_name") or p.get("address_name", "")
                        st.markdown(
                            f"**P {p['place_name']}**"
                            + (f" · {dist}m" if dist else "")
                            + f"  \n<span style='color:#888;font-size:13px;'>{addr}</span>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("주변 주차장 정보가 없습니다.")
            else:
                st.info(f"📍 {stadium_name}\n\n주소: {stadium.get('address', '')}")


        # 탭 3: 추천 준비물
    with tab3:
        rain_prob = weather.get("rain_prob", 0) if 'weather' in dir() else 0

        def prep_card(title, items):
            chips = " ".join([
                f'<span style="display:inline-block; background:#F5F6FA; '
                f'border:1px solid #E8EAF1; border-radius:20px; '
                f'padding:8px 16px; margin:4px 6px 4px 0; font-size:14px; '
                f'color:#2C3144; font-weight:500;">{i}</span>'
                for i in items
            ])
            st.markdown(
                f'<div style="background:#FFFFFF; border:1px solid #E8EAF1; '
                f'border-radius:14px; padding:18px 20px; margin-bottom:16px; '
                f'box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                f'<div style="font-size:16px; font-weight:700; color:#2C3144; '
                f'margin-bottom:12px;">{title}</div>'
                f'<div>{chips}</div></div>',
                unsafe_allow_html=True,
            )

        prep_card("🧳 기본 준비물", [
            "🎟️ 티켓 (모바일 or 실물)", "🪪 신분증", "👟 편한 신발", "💰 현금/카드",
            "📱 보조배터리", "🎽 응원 도구", "🍱 간식 / 음료", "🧴 선크림",
            "🧻 물티슈/휴지"
        ])

        if rain_prob >= 40:
            prep_card("☔ 우천 대비 준비물",
                      ["🌂 우산", "🧥 방수 재킷", "👟 방수 신발", "🛡️ 우비"])

        apps = [
            ("📱", "KBO 공식 앱", "실시간 경기 정보", "https://www.koreabaseball.com"),
            ("🗺️", "카카오맵", "경기장 길 찾기", "https://map.kakao.com"),
            ("🌤️", "기상청 날씨", "실시간 날씨 확인", "https://www.weather.go.kr"),
        ]
        app_cards = "".join([
            f'<a href="{url}" target="_blank" style="text-decoration:none;">'
            f'<div style="background:#FFFFFF; border:1px solid #E8EAF1; '
            f'border-radius:14px; padding:16px 18px; margin-bottom:10px; '
            f'box-shadow:0 1px 3px rgba(0,0,0,0.04); '
            f'display:flex; align-items:center; gap:12px;">'
            f'<span style="font-size:22px;">{emoji}</span>'
            f'<span><span style="font-size:15px; font-weight:700; color:#2C3144;">{name}</span>'
            f'<br><span style="font-size:13px; color:#8A8F9C;">{desc}</span></span>'
            f'</div></a>'
            for emoji, name, desc, url in apps
        ])
        st.markdown(
            '<div style="font-size:16px; font-weight:700; color:#2C3144; '
            'margin:8px 0 12px;">📱 유용한 앱</div>' + app_cards,
            unsafe_allow_html=True,
        )

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
        st.write("### 💺 좌석 가격 (성인 1인 기준)")
        draw_seat_price_table(selected_team)

        st.divider()
        st.write("#### 🗺️ 좌석 배치도")

        team_to_map = {
            "KIA":     "KIA_seat",
            "Samsung": "SAMSUNG_seat",
            "LG":      "DOOSAN LG_seat",
            "Doosan":  "DOOSAN LG_seat",
            "KT":      "KT_seat",
            "SSG":     "SSG_seat",
            "Lotte":   "LOTTE_seat",
            "Hanwha":  "HANHWA_seat",
            "NC":      "NC_seat",
            "Kiwoom":  "KIWOOM_seat",
        }

        map_filename = team_to_map.get(selected_team)

        map_path = None
        if map_filename:
            for ext in [".webp", ".png", ".jpg", ".jpeg"]:
                candidate = Path(BASE_DIR) / "frontend" / "assets" / "stadium_maps" / f"{map_filename}{ext}"
                if candidate.exists():
                    map_path = candidate
                    break

        if map_path:
            import base64
            b64 = base64.b64encode(map_path.read_bytes()).decode()
            suffix = map_path.suffix.lstrip(".").lower()
            mime = "jpeg" if suffix in ("jpg", "jpeg") else suffix
            st.markdown(
                '<div style="background:#fff; border:1px solid #E8EAF1; border-radius:14px; '
                'padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.04); text-align:center;">'
                f'<img src="data:image/{mime};base64,{b64}" '
                'style="max-width:85%; height:auto; border-radius:8px;" /></div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("좌석 배치도를 준비 중입니다.")

