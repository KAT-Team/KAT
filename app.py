import os
import json
import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="KAT - KBO 올인원 직관 도우미",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [JSON 경로 정의] 프로젝트 구조에 맞게 수정 가능합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "kbo_schedule.json")

# 2. 전체 스타일 (라이트 모드 유지)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

/* 사이드바 완전 숨기기 */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* 전체 배경 */
.stApp {
    background-color: #F4F7FA;
    font-family: 'Noto Sans KR', sans-serif;
}

/* 상단 여백 제거 */
.block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* 헤더 숨기기 */
header[data-testid="stHeader"] { display: none !important; }

/* 네비게이션 바 디자인 */
.nav-bar {
    background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
    border-bottom: 3px solid #E8A020;
    padding: 10px 2rem;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
}

.nav-logo-text {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 28px;
    color: #E8A020;
    letter-spacing: 4px;
}

.nav-logo-sub {
    font-size: 11px;
    color: #64748B;
    font-weight: 300;
    letter-spacing: 2px;
}

/* 히어로 섹션 */
.hero {
    background:
        radial-gradient(ellipse at 50% 100%, rgba(232, 160, 32, 0.1) 0%, transparent 60%),
        linear-gradient(180deg, #E0E7FF 0%, #F4F7FA 100%);
    padding: 80px 2rem 60px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero-title {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 56px;
    color: #1E293B;
    line-height: 1.1;
    margin-bottom: 16px;
}

.hero-title span { color: #E8A020; }

.hero-subtitle {
    font-size: 16px;
    color: #64748B;
    font-weight: 400;
    margin-bottom: 48px;
}

.feature-title {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 20px;
    color: #1E293B;
}

.game-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
}

/* 텍스트 색상 고정 */
p, li, span, .stMarkdown { color: #475569 !important; }
h1, h2, h3, h4 { color: #1E293B !important; }

/* 버튼 스타일 */
.stButton > button {
    background-color: white !important;
    color: #475569 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 16px 24px;
}
.stButton > button:hover {
    border-color: #E8A020 !important;
    color: #E8A020 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* 네비게이션 버튼 고정 크기 */
div[data-testid="column"] > div > div > div > button {
    white-space: nowrap !important;
    height: 60px !important;
    font-size: 14px !important;
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태로 현재 페이지 관리
params = st.query_params
if 'page' in params:
    st.session_state.page = params['page']
elif 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 3. 상단 가로형 배너 구성 ---
header_col1, header_col2 = st.columns([1, 4])

with header_col1:
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        padding: 10px 0;
        gap: 12px;
    ">
        <span style="font-size:28px;">⚾</span>
        <div>
            <span class="nav-logo-text">KAT</span>
            <div class="nav-logo-sub">KBO ALL-IN-ONE TOOL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 네비게이션 버튼
    with header_col2:
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)
        with btn_col1:
            if st.button("🏠 홈", use_container_width=True):
                st.session_state.page = 'home'
                st.query_params['page'] = 'home'
                st.rerun()
        with btn_col2:
            if st.button("📅 경기 일정", use_container_width=True):
                st.query_params['page'] = 'schedule'
                st.rerun()
        with btn_col3:
            if st.button("🧭 직관도우미", use_container_width=True):
                st.query_params['page'] = 'guide'
                st.rerun()
        with btn_col4:
            if st.button("🏆 구단 순위", use_container_width=True):
                st.query_params['page'] = 'ranking'
                st.rerun()
        with btn_col5:
            if st.button("🆚 승부 예측", use_container_width=True):
                st.query_params['page'] = 'picks'
                st.rerun()

        st.divider()

# 4. 페이지 라우팅
if st.session_state.page == 'home':
    # 히어로 섹션
    st.markdown("""
    <div class="hero">
        <div class="hero-title">직관의 모든 것,<br><span>KAT</span>에서</div>
        <div class="hero-subtitle">경기 일정 · 티켓 예매 · 날씨 · 교통 · 원정 가이드</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1행: 경기 일정 & 직관 도우미
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if st.button("📅 경기 일정\n\nKBO 10개 구단 일정을 확인하세요.", use_container_width=True):
            st.session_state.page = 'schedule'
            st.rerun()

    with row1_col2:
        if st.button("🧭 직관 도우미\n\n날씨, 교통 가이드 완벽 지원", use_container_width=True):
            st.session_state.page = 'guide'
            st.rerun()

    # 2행: 구단 순위 & 승부 예측
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if st.button("🏆 구단 순위\n\n실시간 KBO 순위표 확인", use_container_width=True):
            st.session_state.page = 'ranking'
            st.rerun()

    with row2_col2:
        if st.button("🆚 승부 예측\n\n실시간 투표율 연동 리워드 예측", use_container_width=True):
            st.session_state.page = 'picks'
            st.rerun()

    st.markdown("### 🏟️ 오늘 예정된 경기")

    LOGO_MAPPING = {
        "KIA": "logo_kia.svg",
        "키움": "logo_kiwoom.svg",
        "한화": "logo_hanwha.svg",
        "NC": "logo_nc.svg",
        "삼성": "logo_samsung.svg",
        "SSG": "logo_ssg.svg",
        "KT": "logo_kt.svg",
        "두산": "logo_doosan.svg",
        "LG": "logo_lg.svg",
        "롯데": "logo_lotte.svg"
    }

    try:
        import base64  # [추가] 이미지를 HTML에 직접 주입하기 위한 라이브러리

        now = pd.Timestamp.now()
        weekday_dict = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

        today_month = str(int(now.strftime("%m")))
        today_day = now.strftime("%m.%d")
        today_week = weekday_dict[now.weekday()]
        target_date_str = f"{today_month}월 {today_day}({today_week})"

        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                all_games = json.load(f)

            today_games = [game for game in all_games if game.get("날짜") == target_date_str]

            if not today_games:
                st.info("오늘 예정된 경기가 없습니다.")
            else:
                cols = st.columns(5)

                for i, game in enumerate(today_games):
                    with cols[i % 5]:
                        match_info = game.get("경기", "정보 없음")
                        time_info = game.get("시간", "-")
                        stadium_info = game.get("구장", "-")

                        # 팀명 분리
                        if "vs" in match_info:
                            away_team, home_team = [team.strip() for team in match_info.split("vs")]
                        elif "VS" in match_info:
                            away_team, home_team = [team.strip() for team in match_info.split("VS")]
                        else:
                            away_team, home_team = match_info, ""

                        # 매핑 파일명 확인
                        away_filename = LOGO_MAPPING.get(away_team, "")
                        home_filename = LOGO_MAPPING.get(home_team, "")

                        # 실제 파일 경로 조립
                        away_local_path = os.path.join(BASE_DIR, "frontend", "assets", away_filename) if away_filename else ""
                        home_local_path = os.path.join(BASE_DIR, "frontend", "assets", home_filename) if home_filename else ""

                        # 1. 원정팀 Base64 인코딩
                        away_src = ""
                        if away_local_path and os.path.exists(away_local_path):
                            with open(away_local_path, "rb") as f_img:
                                away_src = f"data:image/svg+xml;base64,{base64.b64encode(f_img.read()).decode()}"

                        # 2. 홈팀 Base64 인코딩
                        home_src = ""
                        if home_local_path and os.path.exists(home_local_path):
                            with open(home_local_path, "rb") as f_img:
                                home_src = f"data:image/svg+xml;base64,{base64.b64encode(f_img.read()).decode()}"

                        # [최종 해결] Streamlit이 무조건 HTML로 인식하는 테이블 구조로 변경
                        # 높이 500px 원본 로고를 35px 크기로 선명하게 축소하여 정중앙에 수평 정렬합니다.
                        st.markdown(f"""
                        <table style="width:100%; border-collapse:collapse; background-color:#ffffff; border:1px solid #E2E8F0; border-radius:8px; text-align:center; margin-bottom:10px;">
                            <tr style="height:45px;">
                                <td style="width:42%; vertical-align:middle; padding-top:10px;">
                                    <img src="{away_src}" style="height:35px; width:auto; max-width:100%; object-fit:contain; display:block; margin:0 auto;">
                                </td>
                                <td rowspan="2" style="width:16%; vertical-align:middle; font-size:11px; color:#94A3B8; font-weight:800; padding-top:10px;">
                                    VS
                                </td>
                                <td style="width:42%; vertical-align:middle; padding-top:10px;">
                                    <img src="{home_src}" style="height:35px; width:auto; max-width:100%; object-fit:contain; display:block; margin:0 auto;">
                                </td>
                            </tr>
                            <tr>
                                <td style="font-size:13px; color:#475569; font-weight:700; padding-bottom:10px; white-space:nowrap;">
                                    {away_team}
                                </td>
                                <td style="font-size:13px; color:#475569; font-weight:700; padding-bottom:10px; white-space:nowrap;">
                                    {home_team}
                                </td>
                            </tr>
                            <tr>
                                <td colspan="3" style="font-size:12px; color:#64748B; border-top:1px dashed #E2E8F0; padding:6px 0; background-color:#fafafa;">
                                    {stadium_info} <span style="color:#E8A020; font-weight:600;">({time_info})</span>
                                </td>
                            </tr>
                        </table>
                        """, unsafe_allow_html=True)
        else:
            st.error("경기 일정 데이터 파일(JSON)을 찾을 수 없습니다.")

    except Exception as e:
        print(f"로고 렌더링 최종 에러: {e}")
        st.info("경기 데이터를 불러오는 중입니다.")

elif st.session_state.page == 'schedule':
    from frontend.pages.schedule import show
    show()

elif st.session_state.page == 'guide':
    from frontend.pages.guide import show
    show()

elif st.session_state.page == 'ranking':
    from frontend.pages.ranking import show
    show()

elif st.session_state.page == 'picks':
    from frontend.pages.picks import show
    show()
