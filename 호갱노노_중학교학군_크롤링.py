import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

URL = "https://hogangnono.com/"

browser = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
browser.get(URL)
time.sleep(3)

apt_name_list = ["서대문푸르지오센트럴파크", '녹번역e편한세상캐슬', '송파시그니처롯데캐슬', '이수푸르지오더프레티움', '가양역두산위브', '구의자이르네', 
                 '방학동성진뉴파크뷰', '서초그랑자이', '롯데캐슬클라시아', '디에이치포레센트', '답십리엘림퍼스트',
                 '은평서해그랑블', '한울에이치밸리움A동', '자양호반써밋', '구로동 승윤노블리안', '길동 다성이즈빌(387-4)', '이편한세상청계센트럴포레',
                 '독산오르페움타워', '신월동 스위트드림', '상도역롯데캐슬파크엘', '더샵파크프레스티지', '꿈의숲한신더휴', '래미안라클래시', '신림스카이아파트',
                   '힐스테이트세운센트럴2단지', '신림스카이아파트','힐스테이트세운센트럴2단지']

final_df = pd.DataFrame()
for apt_name in apt_name_list_5:

    elem = browser.find_element(By.CLASS_NAME, "keyword")
    elem.send_keys(apt_name)
    elem.send_keys(Keys.ENTER)
    
    time.sleep(1)
    #browser.find_element(By.XPATH, '//*[@id="container"]/div[2]/fieldset/div/div[1]/button[1]').click()
    browser.find_element(By.XPATH, '//*[@id="container"]/div[4]/div/div/div[1]/div/ul/li[1]').click()

    time.sleep(2)

    #아파트이름
    name = browser.find_element(By.XPATH, '//*[@id="container"]/div[4]/div/div/fieldset/div[2]/h1/a').text


    # Generate the dynamic XPaths using the changing parts
    div_part = [19,20, 21, 22, 23, 24]  # List of possible div values
    ul_part = [2, 3, 4]  # List of possible ul values

    # '중학교' 클릭
    base_xpath_1 = '//*[@id="scrollElement"]/div/div[{}]/div/div[1]/div[2]/span'
    for div in div_part:
        xpath_1 = base_xpath_1.format(div)

        try:
            mid_school_click = browser.find_element(By.XPATH, xpath_1)
            browser.execute_script("arguments[0].scrollIntoView();", mid_school_click)
            mid_school_click.click()

        except Exception as e:
            pass
    
    time.sleep(2)
    
    # '더보기' 클릭
    base_xpath_2 = '//*[@id="scrollElement"]/div/div[{}]/div/div[{}]/div/ul/div[{}]/button/span'
    for div in div_part:
        for ul in ul_part:
            # Construct the dynamic XPath
            xpath_2 = base_xpath_2.format(div, 2, ul)
            
            try:
                # Find the element using the constructed XPath
                see_more = browser.find_element(By.XPATH, xpath_2)
                # Now you can interact with the element
                see_more.click()
            except Exception as e:
                # Handle exception if element is not found for this specific XPath
                pass

    time.sleep(2)

    base_xpath_3 = '//*[@id="scrollElement"]/div/div[{}]/div/div[2]/div/div[1]/div[2]/span'
    for div in div_part:
        xpath_3 = base_xpath_3.format(div)

        try: 
            school_group = browser.find_element(By.XPATH, xpath_3)
            browser.execute_script("arguments[0].scrollIntoView();", school_group)
            s_group = school_group.text
        except Exception as e:
            pass

    mid_schools = browser.find_elements(By.CLASS_NAME, 'css-yz0mn.ei9pga10') # 중학교 이름 리스트
    # browser.execute_script("arguments[0].scrollIntoView();", mid_schools)
    element_texts = [element.text for element in mid_schools]

    mid_school_name = []
    rank = []
    rest = []


    for text in element_texts:
        if '중학교' in text:
            mid_school_name.append(text)
        elif '상위' in text:
            rank.append(text)
        elif '-' in text:
            rank.append(text)
        else:
            rest.append(text)

    repeated_list = [s_group] * len(mid_school_name)
    #print(s_group)
    #print(mid_school_name)
    #print(rank)

    df = pd.DataFrame({'학군명' : repeated_list, '학교명' : mid_school_name, '상위' : rank})
    final_df = pd.concat((final_df, df), axis = 0)

    reset = browser.find_element(By.CLASS_NAME, 'btn-reset')
    browser.execute_script("arguments[0].scrollIntoView();", reset)
    reset.click()
    time.sleep(3)

print(final_df)
os.chdir('C:/Users/soyou/Dropbox/대체보고서')
final_df.to_csv('호갱노노_중학교학군.csv', index = False, encoding='utf-8-sig')

    