import argparse
import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_tender_links(driver, max_count):
    driver.get("https://www.b2b-center.ru/market/")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-results-title"))
    )
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.find_all("a", class_="search-results-title", href=True)
    links = ["https://www.b2b-center.ru" + a["href"] for a in cards[:max_count]]
    return links

def parse_tender_detail(driver, url, debug=False):
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "auction_info_td"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        def get_by_id(tag_id):
            tag = soup.find(id=tag_id)
            if tag and tag.find_all("td"):
                return tag.find_all("td")[-1].get_text(strip=True)
            return ""

        def get_from_text(label):
            row = soup.find("td", string=label)
            if row and row.find_next_sibling("td"):
                return row.find_next_sibling("td").get_text(strip=True)
            return ""

        # Название тендера
        name = soup.select_one("div.expandable-text span.value")
        name = name.get_text(strip=True) if name else ""

        # Номер тендера
        headline = soup.find("h1", class_="h3", itemprop="headline")
        number_match = re.search(r'№\s*(\d+)', headline.text) if headline else None
        number = number_match.group(1) if number_match else ""

        price = get_by_id("trade-info-lot-price")
        deadline = get_by_id("trade_info_date_end")
        organizer = get_by_id("trade-info-organizer-name")
        customers = get_from_text("Заказчики:")
        payment = get_from_text("Условия оплаты:")

        if debug:
            print(f"\n Parsed: {number} | {name} | {price} | {deadline}")

        return [number, name, price, deadline, organizer, customers, payment]

    except Exception as e:
        print(f"❌ Ошибка при парсинге {url}: {e}")
        return None

def fetch_all_tenders(max_count, headless=False, debug=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("start-maximized")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    tenders = []

    print(f" Получаем ссылки на {max_count} тендеров...")
    links = get_tender_links(driver, max_count)
    print(f" Найдено {len(links)} ссылок. Получаем подробности...")

    for idx, link in enumerate(links):
        print(f"[{idx + 1}/{len(links)}]  {link}")
        data = parse_tender_detail(driver, link, debug=debug)
        if data:
            tenders.append(data)

    driver.quit()
    return tenders

def main():
    parser = argparse.ArgumentParser(description="CLI-парсер тендеров B2B-Center")
    parser.add_argument("--max", type=int, default=10, help="Макс. количество тендеров")
    parser.add_argument("--output", type=str, default="tenders.csv", help="CSV-файл")
    parser.add_argument("--headless", action="store_true", help="Режим без GUI")
    parser.add_argument("--debug", action="store_true", help="Подробный вывод")

    args = parser.parse_args()

    tenders = fetch_all_tenders(args.max, headless=args.headless, debug=args.debug)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Номер", "Название", "Стоимость", "Дедлайн", "Организатор", "Заказчики", "Оплата"])
        writer.writerows(tenders)

    print(f"\n✅ Сохранено: {len(tenders)} тендеров → {args.output}")

if __name__ == "__main__":
    main()
