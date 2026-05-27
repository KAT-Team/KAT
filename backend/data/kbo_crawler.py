import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def crawl_all_kbo_schedule():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    cleaned_schedule = []

    try:
        url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
        driver.get(url)
        time.sleep(3)

        # 🟢 5월부터 시즌 종료(10월/11월 잔여경기)까지 반복해서 클릭하기
        # 보통 KBO는 3월/4월부터 10월/11월까지 진행됩니다.
        # 안전하게 현재 달인 5월부터 11월까지 순회하도록 설정할게요.
        for month in range(5, 12):
            print(f"📅 {month}월 경기 일정 수집 중...")

            # 1. 원하는 월의 드롭다운 선택창 클릭하기
            try:
                # KBO 페이지 내의 월 선택 dd_month 엘리먼트를 찾아서 해당 월을 선택합니다.
                month_select = driver.find_element(By.ID, "ddlMonth")
                month_select.click()

                # 해당 월의 option 태그를 찾아 클릭 (ex: "05", "06", "07"...)
                month_str = f"{month:02d}"
                option = driver.find_element(By.XPATH, f"//option[@value='{month_str}']")
                option.click()
                time.sleep(2) # 페이지가 새로 고쳐질 때까지 안전하게 대기
            except Exception as e:
                # 만약 11월 일정이 아직 안 열렸거나 없는 달이면 반복문을 종료합니다.
                print(f"✨ {month}월 일정이 없거나 시즌이 종료되어 수집을 마칩니다.")
                break

            # 2. 변경된 페이지의 HTML 긁어오기
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            table = soup.find('table', {'class': 'tbl'})
            if not table:
                continue

            rows = table.find_all('tr')
            current_day = ""

            # 3. 데이터 정제하기
            for row in rows:
                if row.find('th'):
                    continue

                day_tag = row.find('td', {'class': 'day'})
                if day_tag:
                    current_day = day_tag.text.strip()

                time_tag = row.find('td', {'class': 'time'})
                play_tag = row.find('td', {'class': 'play'})

                tds = row.find_all('td')

                if time_tag and play_tag and len(tds) >= 2:
                    stadium = tds[-2].text.strip()

                    if play_tag.find('em'):
                        teams = play_tag.find_all('span')
                        if len(teams) >= 2:
                            matchup = f"{teams[0].text.strip()} vs {teams[-1].text.strip()}"
                    else:
                        matchup = play_tag.text.strip()

                    game_info = {
                        "날짜": f"{month}월 {current_day}", # 몇 월 경기인지 명확하게 구분하기 위해 추가
                        "시간": time_tag.text.strip(),
                        "경기": matchup,
                        "구장": stadium
                    }
                    cleaned_schedule.append(game_info)

        print("---")
        print(f"🎉 전 시즌 일정 실시간 수집 및 전처리 완료!")
        print(f"🔥 총 {len(cleaned_schedule)}개의 경기를 긁어왔습니다.")
        return cleaned_schedule

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    schedule_data = crawl_all_kbo_schedule()

    if schedule_data:
        import json
        with open("kbo_schedule.json", "w", encoding="utf-8") as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=4)
        print("💾 남은 시즌 전체 일정을 kbo_schedule.json에 업데이트 완료!")
