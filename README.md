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

---

## 🚀 주요 기능

### 핵심 기능
| 기능 | 설명 |
|------|------|
| 경기 일정 통합 캘린더 | KBO 10개 구단 경기 일정을 한눈에 확인 |
| 티켓 예매 바로가기 | 구단별 예매 사이트 링크 및 잔여석 안내 |
| 경기 당일 날씨 예보 | 기상청 API 기반 경기장 날씨 및 우천취소 확률 |
| 교통 / 주차 정보 | 카카오맵 API 기반 경기장 주변 교통 및 주차장 안내 |

### 추가 기능
| 기능 | 설명 |
|------|------|
| 직관 체크리스트 | 날씨 기반 준비물 추천 및 우천취소 확률 안내 |
| 좌석 등급 및 가격 비교 | 구단별 좌석 종류와 가격 한눈에 비교 |
| 원정 직관 가이드 | 원정석 위치, 응원 규칙, 경기장 편의시설 안내 |
| 구단 순위 및 최근 전적 | 실시간 KBO 순위표 및 최근 경기 결과 |

---

## 🛠️ 사용한 오픈소스 라이브러리

| 라이브러리 | 용도 | 라이선스 |
|-----------|------|---------|
| [requests](https://requests.readthedocs.io/) | HTTP 요청 (크롤링, API 호출) | Apache 2.0 |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | KBO 경기 일정 HTML 파싱 | MIT |
| [pandas](https://pandas.pydata.org/) | 데이터 처리 및 분석 | BSD |
| [plotly](https://plotly.com/python/) | 데이터 시각화 (캘린더, 차트) | MIT |
| [Streamlit](https://streamlit.io/) | 웹 UI 구성 | Apache 2.0 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 환경변수 관리 | BSD |

---

## 🔑 API 키 발급

| API | 발급 경로 | 비용 |
|-----|---------|------|
| 기상청 단기예보 API | [공공데이터포털](https://www.data.go.kr) 회원가입 후 신청 | 무료 |
| 카카오맵 API | [Kakao Developers](https://developers.kakao.com) 앱 생성 | 무료 |

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

### 5. 실행
```bash
streamlit run app.py
```

---

## 📁 프로젝트 구조

```
KAT/
├── .vscode/
│   ├── settings.json         # VS Code 공통 설정
│   ├── extensions.json       # 추천 확장 프로그램
│   └── launch.json           # Streamlit 디버그 실행 설정
├── backend/
│   ├── data/
│   │   ├── collect.py        # KBO 경기 일정 크롤링
│   │   ├── preprocess.py     # 데이터 전처리
│   │   ├── stadium.py        # 경기장 정보 (예매링크, 좌석, 주소)
│   │   └── weather.py        # 기상청 날씨 API 연동
├── frontend/
│   ├── pages/
│   │   ├── schedule.py       # 경기 일정 캘린더 페이지
│   │   ├── guide.py          # 직관 도우미 페이지
│   │   └── ranking.py        # 구단 순위 페이지
│   └── components/
│       ├── calendar_view.py  # 캘린더 컴포넌트
│       ├── weather_chart.py  # 날씨 시각화
│       ├── seat_chart.py     # 좌석 가격 비교
│       └── ranking_chart.py  # 순위표 차트
├── app.py                    # Streamlit 메인 진입점
├── requirements.txt
├── pyrightconfig.json
├── .env.example
├── .gitignore
└── README.md
```

---

## 🌿 브랜치 전략

```
main                  ← 최종 배포 (직접 push 금지)
develop               ← 통합 개발 (직접 push 금지)
feature/data          ← 팀원 1: 데이터 수집
feature/weather       ← 팀원 1: 날씨 API
feature/viz           ← 팀원 2: 시각화
feature/ui            ← 팀원 3: 웹 UI
```

### 협업 규칙
- 기능 개발 시 반드시 **Issue 먼저 생성** 후 작업 시작
- 작업 완료 후 **PR 올리고 팀원 최소 1명 코드 리뷰** 후 merge
- 본인 PR 본인 merge 금지
- `.env` 파일 push 금지 (API 키 보안)

### 커밋 메시지 규칙
| 태그 | 사용 상황 |
|------|----------|
| `[feat]` | 새로운 기능 추가 |
| `[fix]` | 버그 수정 |
| `[docs]` | 문서 수정 |
| `[refactor]` | 코드 리팩토링 |
| `[chore]` | 기타 작업 |

---

## 👥 팀원

| 이름 | 역할 | 담당 기능 |
|------|------|----------|
| 박소희 | 데이터 & 백엔드 | KBO 크롤링, 날씨 API, 경기장 정보, 데이터 전처리 |
| 박지민 | 시각화 | 캘린더, 순위표, 날씨/좌석 차트 |
| 안주원 | 웹 UI & 통합 | Streamlit UI, 페이지 구성, 통합 및 배포 |

---

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.
