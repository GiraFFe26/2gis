from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
import chromedriver_binary
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys


def collect_data(url):
    ua = UserAgent()
    feeds, names, places, rates, towns_excel = [], [], [], [], []
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument(f'user-agent={ua.random}')
    #chromeOptions.add_argument("--headless")
    chromeOptions.add_argument('window-size=1920x1080')
    chromeOptions.add_argument('--disable-dev-shm-usage')
    chromeOptions.add_argument('--ignore-certificate-errors')
    chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
    chromeOptions.add_argument('--log-level=1')
    chromeOptions.add_argument("--disable-setuid-sandbox")
    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("disable-infobars")
    driver = webdriver.Chrome(options=chromeOptions)
    time.sleep(3.5)
    driver.get(url)
    driver.find_element(By.ID, 'acceptRiskButton').click()
    with open('towns.txt', 'r', encoding='UTF-8') as file:
        towns = [i.strip() for i in file.readlines()]
    your_town = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div/div/div/div/div[1]/div[1]/div[3]/div[1]/h1').text.strip()
    for town in towns:
        text = f'{town} ремонт телефонов'
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]/form/div/input').send_keys(text)
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]/form/div/input').send_keys(Keys.ENTER)
        time.sleep(4.5)
        error = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[1]').text
        if error == 'Точных совпадений нет. Посмотрите похожие места или измените запрос.':
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]/form/div/div/button').click()
            continue
        try:
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/ul/li[1]/div/div[1]/div/input').click()
            time.sleep(2)
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/ul/li[1]/div/div[2]/button[1]/span').click()
            time.sleep(3.5)
        except (ElementNotInteractableException, NoSuchElementException):
            pass
        try:
            src = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div').get_attribute('innerHTML')
        except NoSuchElementException:
            print(town)
            continue
        soup = BeautifulSoup(src, 'lxml')
        k = 0
        to_next = soup.div
        if to_next.get('class') == None:
            k += 1
            rating = to_next.div.div
            if rating.div.text != '':
                rate = int(rating.div.div.div.get('style').split()[-1].split('px')[0]) / 10
                feed = rating.div.text
            elif rating.div.next_sibling != None:
                if rating.div.next_sibling.text != '':
                    rate = int(rating.div.next_sibling.div.div.get('style').split()[-1].split('px')[0]) / 10
                    feed = rating.div.next_sibling.text
            else:
                rate = 0
                feed = 0
            name = rating.next_sibling.find('span').text
            try:
                address = to_next.find('div', class_='_4l12l8').text
            except AttributeError:
                print(town)
                continue
            towns_excel.append(town)
            names.append(name.strip())
            places.append(address.strip())
            rates.append(f'{rate} ★')
            feeds.append(int(feed))
        for item in to_next.next_siblings:
            if item.get('class') == None:
                rating = item.div.div
                if rating.div == None:
                    print(town)
                    continue
                if rating.div.text != '':
                    rate = int(rating.div.div.div.get('style').split()[-1].split('px')[0]) / 10
                    feed = rating.div.text
                elif rating.div.next_sibling != None:
                    if rating.div.next_sibling.text != '':
                        rate = int(rating.div.next_sibling.div.div.get('style').split()[-1].split('px')[0]) / 10
                        feed = rating.div.next_sibling.text
                else:
                    rate = 0
                    feed = 0
                name = rating.next_sibling.find('span').text
                try:
                    address = item.find('div', class_='_4l12l8').text
                except AttributeError:
                    print(town, 'no address')
                    continue
                if your_town in address:
                    break
                towns_excel.append('')
                names.append(name.strip())
                places.append(address.strip())
                rates.append(f'{rate} ★')
                feeds.append(int(feed))
                k += 1
                if k == 12:
                    break
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/div/div[2]/form/div/div/button').click()
    df = pd.DataFrame({'Город': towns_excel,
                       'Название': names,
                       'Адрес': places,
                       'Оценка': rates,
                       'Кол-во отзывов': feeds})
    df.to_excel('2gis.xlsx', index=False)


def main():
    collect_data('https://2gis.ru')


if __name__ == '__main__':
    main()
