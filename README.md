# ⚾ KAT — KBO 올인원 직관 도우미

흩어져 있는 KBO 10개 구단의 경기 일정, 예매 링크, 날씨, 교통 정보를
한 곳에서 볼 수 있는 직관 준비 웹서비스입니다.

---

## 📌 프로젝트 소개

야구 팬들이 직관을 준비할 때 겪는 불편함에서 출발했습니다.
- 구단마다 예매 사이트가 달라 일일이 찾아야 하는 불편함
- 경기 일정, 날씨, 교통 정보가 여러 곳에 흩어져 있는 문제
- 원정 직관 시 낯선 경기장 정보를 파악하기 어려운 점

KAT는 이 모든 정보를 한 곳에서 제공합니다.

여기에 더해, 단순한 정보 제공을 넘어 야구를 더 재미있게 즐길 수 있도록
실시간 팀 스탯 기반 승부 예측 시뮬레이션과 유저 참여형 투표 기능을 추가로 제공합니다.
경기 전 승리 확률을 예측해보고, 다른 팬들과 함께 승부를 예측하는 색다른 직관 경험을 즐겨보세요.
---

## 🚀 주요 기능

### 핵심 기능
| 기능 | 설명 |
|------|------|
| 경기 일정 통합 캘린더 | KBO 10개 구단 경기 일정을 JSON 데이터 기반으로 한눈에 확인 |
| 티켓 예매 바로가기 | 구단별 예매 사이트 링크 및 잔여석 안내 |
| 경기 당일 날씨 예보 | 기상청 단기예보 API 기반 경기장 날씨 및 강수 확률 안내 |
| 교통 / 주차 정보 | 카카오맵 API 기반 경기장 위치 및 주변 주차장(반경 1km) 안내 |

### 추가 기능
| 기능 | 설명 |
|------|------|
| 직관 체크리스트 | 날씨 기반 준비물 추천 및 우천 대비 안내 |
| 좌석 등급 및 가격 비교 | 구단별 좌석 종류, 가격 및 좌석 배치도 이미지 제공 |
| 원정 직관 가이드 | 원정석 위치, 응원 규칙, 경기장 편의시설 안내 |
| 구단 순위 | 실시간 KBO 순위표 및 가을야구 진출권(상위 5팀) 하이라이트 |
| 승부 예측 시뮬레이션 | 6가지 통계 파라미터 기반 경기 승리 확률 예측 |
| 유저 승부 예측 투표 | 닉네임 기반 투표 참여 및 배당률 연동 포인트 시스템 |

---

## 🤖 승부예측 알고리즘

AI/ML 모델 없이 실시간 크롤링 데이터 기반 순수 통계 계산으로 승리 확률을 예측합니다.

| 파라미터 | 설명 |
|---------|------|
| 기본 승률 | 시즌 누적 팀 승률 기반 확률 계산 |
| 홈/원정 분리 승률 | 고정 홈 어드밴티지 대신 실제 홈/원정 승률 차이 반영 |
| 투수 컨디션 | 선발투수 당일 컨디션 (0~100점) 반영 |
| 투수 ERA | 선발투수 평균자책점 기반 보정 |
| 득점/실점 차이 | 시즌 누적 팀 득점력 및 실점 차이 반영 |
| OPS | 팀 타격 파워 지표 (출루율 + 장타율) 반영 |

---

## 📡 데이터 수집

| 데이터 | 출처 | 방식 |
|--------|------|------|
| 팀 순위, 승률, 홈/원정 승률 | KBO 공식 사이트 | requests + BeautifulSoup 크롤링 |
| 팀 타율, 득점, OPS | KBO 공식 사이트 | requests + BeautifulSoup 크롤링 |
| 팀 ERA, 실점 | KBO 공식 사이트 | requests + BeautifulSoup 크롤링 |
| 경기 일정 | KBO 공식 사이트 | Selenium 동적 크롤링 → JSON 저장 |
| 당일/시즌 경기 결과 | 네이버 스포츠 API | REST API |
| 경기장 날씨 | 기상청 단기예보 API (data.go.kr) | REST API |
| 경기장 지도/주차장 | 카카오맵 API | REST API |

> ⚠️ KBO 및 네이버 스포츠 데이터는 학교 프로젝트(비상업적) 목적으로만 활용하며, 실제 서비스화 시에는 공식 라이선스 계약을 통해 데이터를 제공받을 예정입니다.

---

## 🛠️ 사용한 오픈소스 라이브러리

| 라이브러리 | 용도 | 라이선스 |
|-----------|------|---------|
| [requests](https://requests.readthedocs.io/) | HTTP 요청 (크롤링, API 호출) | Apache 2.0 |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | KBO 팀 스탯 HTML 파싱 | MIT |
| [selenium](https://www.selenium.dev/) | KBO 경기 일정 동적 크롤링 | Apache 2.0 |
| [pandas](https://pandas.pydata.org/) | 데이터 처리 및 분석 | BSD |
| [plotly](https://plotly.com/python/) | 데이터 시각화 (차트) | MIT |
| [Streamlit](https://streamlit.io/) | 웹 UI 구성 | Apache 2.0 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 환경변수 관리 | BSD |

---

## 🔑 API 키 발급

| API | 발급 경로 | 비용 |
|-----|---------|------|
| 기상청 단기예보 API | [공공데이터포털(data.go.kr)](https://www.data.go.kr) 회원가입 후 신청 (**기상청 허브 API 아님**) | 무료 |
| 카카오맵 JavaScript API | [Kakao Developers](https://developers.kakao.com) 앱 생성 후 **JavaScript 키** 발급 (REST 키와 다름) | 무료 |
| 카카오 로컬 REST API | 동일 앱에서 **REST API 키** 별도 발급 | 무료 |

---

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/KAT-Team/KAT.git
cd KAT
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
cp .env.example .env
# .env 파일 열어서 API 키 입력
```

`.env` 파일 예시:
```
WEATHER_API_KEY=기상청_API_키
KAKAO_MAP_API_KEY=카카오_JavaScript_키
KAKAO_REST_KEY=카카오_REST_API_키
```

### 5. 경기 일정 크롤링 (최초 1회 실행)
```bash
python3 backend/data/kbo_crawler.py
```

### 6. 실행
```bash
streamlit run app.py
```

---

## 📁 프로젝트 구조

```
KAT/
├── backend/
│   ├── data/
│   │   ├── collect.py              # 구단 정보, 예매 링크
│   │   ├── stadium.py              # 경기장 정보 (좌석, 주소, 좌표)
│   │   ├── weather.py              # 기상청 날씨 API 연동
│   │   ├── team_crawler.py         # KBO 팀 순위/타율/ERA/OPS 크롤링
│   │   ├── team_stats.py           # 팀 스탯 및 선발투수 데이터 (폴백용)
│   │   ├── kbo_crawler.py          # KBO 경기 일정 Selenium 크롤링
│   │   ├── naver_game_crawler.py   # 네이버 API 경기 결과 크롤링
│   │   └── vote_manager.py         # 닉네임 기반 투표 관리
│   └── simulation/
│       └── predict.py              # 승리 확률 예측 알고리즘
├── frontend/
│   ├── pages/
│   │   ├── schedule.py             # 경기 일정 캘린더 페이지
│   │   ├── guide.py                # 직관 도우미 페이지
│   │   ├── ranking.py              # 구단 순위 페이지
│   │   └── picks.py                # 승부 예측 페이지
│   ├── components/
│   │   ├── calendar_view.py        # 캘린더 컴포넌트
│   │   ├── weather_chart.py        # 날씨 시각화
│   │   ├── seat_chart.py           # 좌석 가격 비교
│   │   └── ranking_chart.py        # 순위표 차트
│   └── assets/
│       ├── stadium_maps/           # 구단별 좌석 배치도 이미지
│       └── logo_*.svg              # 구단 로고
├── kbo_schedule.json               # KBO 경기 일정 데이터 (크롤링 결과)
├── votes.json                      # 투표 데이터 (자동 생성)
├── app.py                          # Streamlit 메인 진입점
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🌿 브랜치 전략

```
main                  ← 최종 배포 (직접 push 금지)
develop               ← 통합 개발 (직접 push 금지)
feature/data_crawling ← 팀 스탯 크롤링, 시뮬레이션
feature/weather       ← 날씨 API 연동
feature/pages         ← 페이지 UI 개발
feature/fix           ← 버그 수정
feature/*             ← 기타 기능별 개발 브랜치
```

### 협업 규칙
- 기능 개발 시 반드시 `feature/` 브랜치에서 작업
- 작업 완료 후 PR 올리고 팀원 최소 1명 코드 리뷰 후 merge
- 본인 PR 본인 merge 금지
- `.env` 파일 push 금지 (API 키 보안)

### 커밋 메시지 규칙
| 태그 | 사용 상황 |
|------|----------|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `refactor` | 코드 리팩토링 |
| `chore` | 기타 작업 |

---

## 👥 팀원

| 이름 | 역할 | 담당 기능 |
|------|------|----------|
| 박소희 | 팀장 / 데이터 & 백엔드 | KBO 크롤링, 날씨 API, 승부예측 알고리즘, 구단 순위 |
| 박지민 | 시각화 | 캘린더, 순위표, 날씨/좌석 차트, UI 개선 |
| 안주원 | 웹 UI & 통합 | Streamlit UI, 승부예측 페이지, 통합 및 배포 |

---

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.
