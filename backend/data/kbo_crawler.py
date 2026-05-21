import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def crawl_kbo_schedule():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
        driver.get(url)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 1. 일정 테이블 찾기
        table = soup.find('table', {'class': 'tbl'})
        if not table:
            print("❌ 테이블을 찾지 못했습니다.")
            return None

        # 🔥 [수정 핵심] tbody가 없어도 안전하게 모든 행(tr)을 가져오도록 변경
        rows = table.find_all('tr')

        cleaned_schedule = []
        current_day = ""

        # 2. 행을 하나씩 돌면서 딱 필요한 텍스트만 추출
        for row in rows:
            # th만 있는 제목 행(헤더)은 데이터가 없으므로 건너뜁니다.
            if row.find('th'):
                continue

            day_tag = row.find('td', {'class': 'day'})
            if day_tag:
                current_day = day_tag.text.strip()

            time_tag = row.find('td', {'class': 'time'})
            play_tag = row.find('td', {'class': 'play'})

            tds = row.find_all('td')

            # 유효한 경기 데이터 행인지 체크
            if time_tag and play_tag and len(tds) >= 2:
                stadium = tds[-2].text.strip() # 구장 정보 추출

                # 팀 이름만 깔끔하게 분리
                if play_tag.find('em'):
                    teams = play_tag.find_all('span')
                    if len(teams) >= 2:
                        matchup = f"{teams[0].text.strip()} vs {teams[-1].text.strip()}"
                else:
                    matchup = play_tag.text.strip()

                game_info = {
                    "날짜": current_day,
                    "시간": time_tag.text.strip(),
                    "경기": matchup,
                    "구장": stadium
                }
                cleaned_schedule.append(game_info)

        print("🎉 불필요한 데이터 제거 완료! 깔끔한 일정만 수집 성공!")
        print(f"총 {len(cleaned_schedule)}개의 경기를 가져왔습니다.")

        # 샘플로 상위 5개만 출력
        for game in cleaned_schedule:
            print(game)

        return cleaned_schedule

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_kbo_schedule()
