import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
from html_table_parser import parser_functions
import pandas as pd
import os
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.applyhome.co.kr/co/coa/selectMainView.do"

browser = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
browser.get(URL)

# remove AD popup
#find = browser.find_element(By.XPATH, '//*[@id="pop_info"]/div/div/div[2]/div[2]/button')
#find.click()

# 분양정보/경쟁률
find = browser.find_element(By.XPATH, '//*[@id="tab1"]/ul/li[1]/a')
find.click()

# 연도 지정하기
start_year = browser.find_element(By.XPATH, '//*[@id="start_year"]')
start_year.click()
year_1 = browser.find_element(By.XPATH, '//*[@id="start_year"]/option[35]') #21년 9월 : 23 / 20년 9월 : 35 / 19년 9월 : 47 / 18년 9월 : 59
browser.execute_script("arguments[0].scrollIntoView(true);", year_1)
year_1.click()

end_year = browser.find_element(By.XPATH, '//*[@id="end_year"]')
end_year.click()
year_2 = browser.find_element(By.XPATH, '//*[@id="end_year"]/option[25]') # 22년 8월 : 13 / 21년 8월 : 25 / 20년 8월 : 37 / 19년 8월 : 49
browser.execute_script("arguments[0].scrollIntoView(true);", year_2) 
year_2.click()

# 주택 구분
#type = browser.find_element(By.XPATH, '//*[@id="cate01"]')
#type.click()
#type_pv = browser.find_element(By.XPATH, '//*[@id="cate01"]/option[2]') # 민영 선택
#type_pv.click()

# 조회
check = browser.find_element(By.XPATH, '//*[@id="pbSearchForm"]/div[2]/button')
check.click()

# open the pop-up window
# browser.find_element(By.CSS_SELECTOR, "#subContent > div.mt_10 > table > tbody > tr:nth-child(1) > td.txt_l > a").click()
# browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click() 

# browser.find_element(By.CSS_SELECTOR, "#subContent > div.mt_10 > table > tbody > tr:nth-child(2) > td.txt_l > a").click()

# current page
curPage = 1
round = 1

# entire page
totalPage = 10
totalRound = 40

page_df = pd.DataFrame()
final_df = pd.DataFrame()
while curPage <= totalPage:
    try:
        for i in range(1, 11):
            try:

                browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

                browser.switch_to.frame("iframeDialog")
                # find and scrape the element(s) in the pop-up window
                apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
                date = browser.find_element(By.XPATH, '//*[@id="printArea"]/ul[3]/li[1]').text
                date_cleaned = date.replace('* 입주예정월 :', '')

                d = {'아파트이름' : [apt_name], '입주예정월' : [date_cleaned]}
                df = pd.DataFrame(data = d)
                print(apt_name)

                page_df = pd.concat((page_df, df), axis = 0)
                    
                browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
                browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()

            except NoSuchElementException:
                    print(f"Element for row {i} not found. Skipping...")
                    break
        

        # 페이지 수 증가
        curPage += 1
        if curPage > totalPage:
            browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click() # 화살표 누르기
            curPage = 1
        if round > totalRound:
            break
        
        # 페이지 이동 클릭
        cur_css = '#paging > div > a:nth-child({})'.format(curPage)
        browser.find_element(By.CSS_SELECTOR, cur_css).click()
    
    except NoSuchElementException:
        print("Table or element not found")
        break
 
os.chdir('C:/Users/soyou/Desktop/python/web crawling')
page_df.to_csv('입주예정일_2009-2108_전체.csv', index = False, encoding='utf-8-sig')