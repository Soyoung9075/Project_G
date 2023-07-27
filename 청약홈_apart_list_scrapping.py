
#################### 2021년 9월 ~ 2022년 8월 ######################
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

browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get(URL)

# remove AD popup
#find = browser.find_element(By.XPATH, '//*[@id="pop_info"]/div/div/div[2]/div[2]/button')
#find.click()

# 분양정보/경쟁률
find = browser.find_element(By.XPATH, '//*[@id="tab1"]/ul/li[1]/a')
find.click()

# open the pop-up window
# browser.find_element(By.CSS_SELECTOR, "#subContent > div.mt_10 > table > tbody > tr:nth-child(1) > td.txt_l > a").click()
# browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click() 

# browser.find_element(By.CSS_SELECTOR, "#subContent > div.mt_10 > table > tbody > tr:nth-child(2) > td.txt_l > a").click()

# 연도 지정하기
start_year = browser.find_element(By.XPATH, '//*[@id="start_year"]')
start_year.click()
year_1 = browser.find_element(By.XPATH, '//*[@id="start_year"]/option[23]') #2021년 9월
browser.execute_script("arguments[0].scrollIntoView(true);", year_1)
year_1.click()

end_year = browser.find_element(By.XPATH, '//*[@id="end_year"]')
end_year.click()
year_2 = browser.find_element(By.XPATH, '//*[@id="end_year"]/option[13]') #2022년 8월
browser.execute_script("arguments[0].scrollIntoView(true);", year_2)
year_2.click()

# 조회
check = browser.find_element(By.XPATH, '//*[@id="pbSearchForm"]/div[2]/button')
check.click()
############################## 1 ~ 10 #######################################
# current page
curPage = 1

# entire page
totalPage = 10

real_final_df_1 = pd.DataFrame()
while curPage <= totalPage:

    final_df = pd.DataFrame()
    for i in range(1, 11):
        browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

        browser.switch_to.frame("iframeDialog")
        # find and scrape the element(s) in the pop-up window
        apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
        location = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[1]/td[2]').text
        n_of_apt = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[2]/td[2]').text

        d = {'아파트이름' : [apt_name], '공급위치' : [location], '공급세대' : [n_of_apt]}
        df1 = pd.DataFrame(data = d)

        # 공급면적/공급가 table이 대부분 5번째이나 예외적으로 4번쨰인 경우
        if len(browser.find_elements(By.TAG_NAME, 'table')) == 6:
            table = browser.find_elements(By.TAG_NAME, 'table')[4]
        else :
            table = browser.find_elements(By.TAG_NAME, 'table')[3]

        rows = table.find_elements(By.TAG_NAME, "tr")
        table_data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            for cell in cells:
                if cell.text != '청약통장으로 청약(청약금 없음)':
                    row_data.append(cell.text)
            table_data.append(row_data)
        df2 = pd.DataFrame(table_data, columns =['공급면적', '공급금액']) 

        for i in range(len(rows)-2):
            df1 = df1.append(df1.loc[i], ignore_index = True)
        
        temp = pd.concat((df1, df2), axis = 1)

        final_df = pd.concat((final_df, temp), axis = 0)
        
        browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
        browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()
 
    real_final_df_1 = pd.concat((real_final_df_1, final_df), axis = 0)
    
    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed')
        break

        
    # 페이지 이동 클릭
    cur_css = '#paging > div > a:nth-child({})'.format(curPage)
    WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)
   
###################### 11~20 #######################################
# 화살표 누르기
browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click()
# current page
curPage = 1

# entire page
totalPage = 10

real_final_df_2 = pd.DataFrame()
while curPage <= totalPage:

    final_df = pd.DataFrame()
    for i in range(1, 11):
        browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

        browser.switch_to.frame("iframeDialog")
        # find and scrape the element(s) in the pop-up window
        apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
        location = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[1]/td[2]').text
        n_of_apt = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[2]/td[2]').text

        d = {'아파트이름' : [apt_name], '공급위치' : [location], '공급세대' : [n_of_apt]}
        df1 = pd.DataFrame(data = d)

        # 공급면적/공급가 table이 대부분 5번째이나 예외적으로 4번쨰인 경우
        if len(browser.find_elements(By.TAG_NAME, 'table')) == 6:
            table = browser.find_elements(By.TAG_NAME, 'table')[4]
        else :
            table = browser.find_elements(By.TAG_NAME, 'table')[3]

        rows = table.find_elements(By.TAG_NAME, "tr")
        table_data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            for cell in cells:
                if cell.text != '청약통장으로 청약(청약금 없음)':
                    row_data.append(cell.text)
            table_data.append(row_data)
        df2 = pd.DataFrame(table_data, columns =['공급면적', '공급금액']) 

        for i in range(len(rows)-2):
            df1 = df1.append(df1.loc[i], ignore_index = True)
        
        temp = pd.concat((df1, df2), axis = 1)

        final_df = pd.concat((final_df, temp), axis = 0)
        
        browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
        browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()
 
    real_final_df_2 = pd.concat((real_final_df_2, final_df), axis = 0)

    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed')
        break

    # 페이지 이동 클릭
    cur_css = '#paging > div > a:nth-child({})'.format(curPage)
    WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)

###################### 21~30 #######################################
# 화살표 누르기
browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click()
# current page
curPage = 1

# entire page
totalPage = 10

real_final_df_3 = pd.DataFrame()
while curPage <= totalPage:

    final_df = pd.DataFrame()
    for i in range(1, 11):
        browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

        browser.switch_to.frame("iframeDialog")
        # find and scrape the element(s) in the pop-up window
        apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
        location = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[1]/td[2]').text
        n_of_apt = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[2]/td[2]').text

        d = {'아파트이름' : [apt_name], '공급위치' : [location], '공급세대' : [n_of_apt]}
        df1 = pd.DataFrame(data = d)

        # 공급면적/공급가 table이 대부분 5번째이나 예외적으로 4번쨰인 경우
        if len(browser.find_elements(By.TAG_NAME, 'table')) == 6:
            table = browser.find_elements(By.TAG_NAME, 'table')[4]
        else :
            table = browser.find_elements(By.TAG_NAME, 'table')[3]

        rows = table.find_elements(By.TAG_NAME, "tr")
        table_data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            for cell in cells:
                if cell.text != '청약통장으로 청약(청약금 없음)':
                    row_data.append(cell.text)
            table_data.append(row_data)
        df2 = pd.DataFrame(table_data, columns =['공급면적', '공급금액']) 

        for i in range(len(rows)-2):
            df1 = df1.append(df1.loc[i], ignore_index = True)
        
        temp = pd.concat((df1, df2), axis = 1)

        final_df = pd.concat((final_df, temp), axis = 0)
        
        browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
        browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()
 
    real_final_df_3 = pd.concat((real_final_df_3, final_df), axis = 0)

    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed')
        break

    # 페이지 이동 클릭
    cur_css = '#paging > div > a:nth-child({})'.format(curPage)
    WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)

###################### 31~40 #######################################
# 화살표 누르기
browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click()
# current page
curPage = 1

# entire page
totalPage = 10

real_final_df_4 = pd.DataFrame()
while curPage <= totalPage:

    final_df = pd.DataFrame()
    for i in range(1, 11):
        browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

        browser.switch_to.frame("iframeDialog")
        # find and scrape the element(s) in the pop-up window
        apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
        location = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[1]/td[2]').text
        n_of_apt = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[2]/td[2]').text

        d = {'아파트이름' : [apt_name], '공급위치' : [location], '공급세대' : [n_of_apt]}
        df1 = pd.DataFrame(data = d)

        # 공급면적/공급가 table이 대부분 5번째이나 예외적으로 4번쨰인 경우
        if len(browser.find_elements(By.TAG_NAME, 'table')) == 6:
            table = browser.find_elements(By.TAG_NAME, 'table')[4]
        else :
            table = browser.find_elements(By.TAG_NAME, 'table')[3]

        rows = table.find_elements(By.TAG_NAME, "tr")
        table_data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            for cell in cells:
                if cell.text != '청약통장으로 청약(청약금 없음)':
                    row_data.append(cell.text)
            table_data.append(row_data)
        df2 = pd.DataFrame(table_data, columns =['공급면적', '공급금액']) 

        for i in range(len(rows)-2):
            df1 = df1.append(df1.loc[i], ignore_index = True)
        
        temp = pd.concat((df1, df2), axis = 1)

        final_df = pd.concat((final_df, temp), axis = 0)
        
        browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
        browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()
 
    real_final_df_4 = pd.concat((real_final_df_4, final_df), axis = 0)

    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed')
        break

    # 페이지 이동 클릭
    cur_css = '#paging > div > a:nth-child({})'.format(curPage)
    WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)


###################### 41~45 #######################################
# 화살표 누르기
browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click()
# current page
curPage = 1

# entire page
totalPage = 9

real_final_df_5 = pd.DataFrame()
while curPage <= totalPage:

    final_df = pd.DataFrame()
    for i in range(1, 11):
        try:
    
            # Click on the element if it exists
            #element = WebDriverWait(browser, 10).until(
                #EC.element_to_be_clickable((By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a'))
            #)
            #element.click()
            browser.find_element(By.CSS_SELECTOR, '#subContent > div.mt_10 > table > tbody > tr:nth-child(' + str(i) + ') > td.txt_l > a').click()

            browser.switch_to.frame("iframeDialog")
            # find and scrape the element(s) in the pop-up window
            apt_name = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/thead/tr/th').text
            location = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[1]/td[2]').text
            n_of_apt = browser.find_element(By.XPATH, '//*[@id="printArea"]/table[1]/tbody/tr[2]/td[2]').text

            d = {'아파트이름' : [apt_name], '공급위치' : [location], '공급세대' : [n_of_apt]}
            df1 = pd.DataFrame(data = d)

            # 공급면적/공급가 table이 대부분 5번째이나 예외적으로 4번쨰인 경우
            if len(browser.find_elements(By.TAG_NAME, 'table')) == 6:
                table = browser.find_elements(By.TAG_NAME, 'table')[4]
            else :
                table = browser.find_elements(By.TAG_NAME, 'table')[3]

            rows = table.find_elements(By.TAG_NAME, "tr")
            table_data = []
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = []
                for cell in cells:
                    if cell.text != '청약통장으로 청약(청약금 없음)':
                        row_data.append(cell.text)
                table_data.append(row_data)
            df2 = pd.DataFrame(table_data, columns =['공급면적', '공급금액']) 

            for i in range(len(rows)-2):
                df1 = df1.append(df1.loc[i], ignore_index = True)
        
            temp = pd.concat((df1, df2), axis = 1)

            final_df = pd.concat((final_df, temp), axis = 0)
            print(apt_name)
        
            browser.switch_to.default_content() # iframe에서 빠져나오기 ==> 반드시 해줘야 팝업을 끄고 다음 리스트로 넘어갈 수 있음. 
            browser.find_element(By.XPATH, '/html/body/div[4]/div/button/span[1]').click()

        except NoSuchElementException:
            print(f"Element for row {i} not found. Skipping...")
            break
 
    real_final_df_5 = pd.concat((real_final_df_5, final_df), axis = 0)

    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed')
        break

    # 페이지 이동 클릭
    cur_css = '#paging > div > a:nth-child({})'.format(curPage)
    WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)


final_file = pd.concat((real_final_df_1, real_final_df_2, real_final_df_3,real_final_df_4,real_final_df_5), axis = 0)
# 저장하기
os.chdir('C:/Users/soyou/Desktop/python/web crawling')
final_file.to_csv('apart_list_new_2109-2208.csv', index = False, encoding='utf-8-sig')
