from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

CHROMEDRIVER_PATH = "./chromedriver.exe"
JIRA_GROUPS_URL = "https://YOUR_DOMAIN.atlassian.net/admin/groups"  # ← Укажи свой домен

options = Options()
# options.add_argument("--headless")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get(JIRA_GROUPS_URL)
print("🔐 Открой браузер, войди в Atlassian, перейди в Directory > Groups и нажми Enter...")
input()  # Ждем ручного логина

group_names = []
group_descriptions = []

def scrape_current_page():
    rows = driver.find_elements(By.CSS_SELECTOR, "tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            lines = cols[0].text.strip().splitlines()
            name = lines[0] if len(lines) > 0 else ""
            description = lines[1] if len(lines) > 1 else ""
            if name and name not in group_names:
                group_names.append(name)
                group_descriptions.append(description)

while True:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        scrape_current_page()

        # Ищем стрелку "вперёд" в пагинации
        next_button = driver.find_element(By.XPATH, '//nav//button[.//svg]')
        if next_button.get_attribute("disabled"):
            print("⛔ Последняя страница.")
            break

        next_button.click()
        time.sleep(2)

    except Exception as e:
        print(f"⚠️ Остановка по ошибке: {e}")
        break

driver.quit()

df = pd.DataFrame({
    "Group Name": group_names,
    "Description": group_descriptions
})
df.to_excel("jira_groups.xlsx", index=False)
print("✅ Готово! Файл 'jira_groups.xlsx' сохранён.")
