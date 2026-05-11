import streamlit as st
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(
    page_title="KAT - KBO 올인원 직관 도우미",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

/* 카드 스타일 */
.feature-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 32px 24px;
    text-align: center;
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
}
.stButton > button:hover {
    border-color: #E8A020 !important;
    color: #E8A020 !important;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태로 현재 페이지 관리
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 3. 상단 가로형 배너 구성 ---
# 로고와 네비게이션 버튼을 한 줄(columns)로 배치
header_col1, header_col2 = st.columns([1, 2])

with header_col1:
    # 로고 부분
    st.markdown("""
    <div style="padding-top: 10px;">
        <span style="font-size:28px;">⚾</span>
        <span class="nav-logo-text">KAT</span>
        <div class="nav-logo-sub">KBO ALL-IN-ONE TICKET GUIDE</div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # 네비게이션 버튼 가로 배치
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        if st.button("🏠 홈", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
    with btn_col2:
        if st.button("📅 경기 일정", use_container_width=True):
            st.session_state.page = 'schedule'
            st.rerun()
    with btn_col3:
        if st.button("🧭 직관 도우미", use_container_width=True):
            st.session_state.page = 'guide'
            st.rerun()
    with btn_col4:
        if st.button("🏆 구단 순위", use_container_width=True):
            st.session_state.page = 'ranking'
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

    # 기능 카드 (3열 가로 배치)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h3>📅 경기 일정</h3><p>KBO 10개 구단 일정을 확인하세요.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>🧭 직관 도우미</h3><p>날씨, 교통 가이드 완벽 지원</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>🏆 구단 순위</h3><p>실시간 KBO 순위표 확인</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("오늘의 경기")

    try:
        # collect.py에서 데이터 가져오기
        from backend.data.collect import get_today_games, TEAMS
        today_games = get_today_games()
        if today_games.empty:
            st.info("오늘 예정된 경기가 없습니다.")
        else:
            for _, game in today_games.iterrows():
                home = TEAMS.get(game['home_team'], game['home_team'])
                away = TEAMS.get(game['away_team'], game['away_team'])
                st.markdown(f"""
                <div class="game-card">
                    <span style="font-weight:700;">{away} VS {home}</span> | 📍 {game['stadium']} ({game['time']})
                </div>
                """, unsafe_allow_html=True)
    except Exception:
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
